from abc import ABC, abstractmethod
import asyncio
from enum import IntEnum, IntFlag
import itertools
from logging import Logger
import struct
from typing import Any, NamedTuple, cast
import dolphin_memory_engine  # type: ignore
import subprocess
import Utils

GC_GAME_ID_ADDRESS = 0x80000000


class GameCubeException(Exception):
    pass


class DolphinException(GameCubeException):
    pass


class NintendontException(GameCubeException):
    pass


class GameCubeClient(ABC):
    @abstractmethod
    def is_connected(self):
        ...

    @abstractmethod
    async def connect(self):
        ...

    @abstractmethod
    async def disconnect(self):
        ...

    @abstractmethod
    async def read_pointer(self, pointer: int, offset: int, byte_count: int) -> Any:
        ...

    @abstractmethod
    async def read_address(self, address: int, bytes_to_read: int) -> Any:
        ...

    @abstractmethod
    async def write_pointer(self, pointer: int, offset: int, data: Any):
        ...

    @abstractmethod
    async def write_address(self, address: int, data: Any):
        ...


class DolphinClient(GameCubeClient):
    dolphin: dolphin_memory_engine  # type: ignore
    logger: Logger

    def __init__(self, logger: Logger):
        self.dolphin = dolphin_memory_engine
        self.logger = logger

    def is_connected(self):
        try:
            self.__assert_connected()
            return True
        except Exception:
            return False

    async def connect(self):
        if not self.dolphin.is_hooked():
            self.dolphin.hook()
        if not self.dolphin.is_hooked():
            raise DolphinException(
                "Could not connect to Dolphin, verify that you have a game running in the emulator"
            )

    def __disconnect(self):
        if self.dolphin.is_hooked():
            self.dolphin.un_hook()

    async def disconnect(self):
        self.__disconnect()

    def __assert_connected(self):
        """Custom assert function that returns a DolphinException instead of a generic RuntimeError if the connection is lost"""
        try:
            self.dolphin.assert_hooked()
            # For some reason the dolphin_memory_engine.is_hooked() function doesn't recognize when the game is closed, checking if memory is available will assert the connection is alive
            self.dolphin.read_bytes(GC_GAME_ID_ADDRESS, 1)
        except RuntimeError as e:
            self.__disconnect()
            raise DolphinException(e)

    async def verify_target_address(self, target_address: int, read_size: int):
        """Ensures that the target address is within the valid range for GC memory"""
        if target_address < 0x80000000 or target_address + read_size > 0x81800000:
            raise DolphinException(
                f"{target_address:x} -> {target_address + read_size:x} is not a valid for GC memory"
            )

    async def read_pointer(self, pointer: int, offset: int, byte_count: int) -> Any:
        self.__assert_connected()

        address = None
        try:
            address = self.dolphin.follow_pointers(pointer, [0])
        except RuntimeError:
            return None

        if not self.dolphin.is_hooked():
            raise DolphinException("Dolphin no longer connected")

        address += offset
        return await self.read_address(address, byte_count)

    async def read_address(self, address: int, bytes_to_read: int) -> Any:
        self.__assert_connected()
        self.verify_target_address(address, bytes_to_read)
        result = self.dolphin.read_bytes(address, bytes_to_read)
        return result

    async def write_pointer(self, pointer: int, offset: int, data: Any):
        self.__assert_connected()
        address = None
        try:
            address = self.dolphin.follow_pointers(pointer, [0])
        except RuntimeError:
            return None

        if not self.dolphin.is_hooked():
            raise DolphinException("Dolphin no longer connected")

        address += offset
        return await self.write_address(address, data)

    async def write_address(self, address: int, data: Any):
        self.__assert_connected()
        result = self.dolphin.write_bytes(address, data)
        return result


def assert_no_running_dolphin() -> bool:
    """Only checks on windows for now, verifies no existing instances of dolphin are running."""
    if Utils.is_windows:
        if get_num_dolphin_instances() > 0:
            return False
    return True


def get_num_dolphin_instances() -> int:
    """Only checks on windows for now, kind of brittle so if it causes problems then just ignore it"""
    try:
        if Utils.is_windows:
            output = subprocess.check_output("tasklist", shell=True).decode()
            lines = output.strip().split("\n")
            count = sum("Dolphin.exe" in line for line in lines)
            return count
        return 0
    except:
        return 0


NINTENDONT_PORT = 43673


class NintendontMemoryOperationType(IntEnum):
    READ_COMMANDS = 0
    REQUEST_VERSION = 1


class NintendontOperationHeader(IntFlag):
    HAS_READ = 0x80
    HAS_WRITE = 0x40
    IS_WORD = 0x20
    HAS_OFFSET = 0x10
    ADDRESS_INDEX_MASK = 0xF

    @classmethod
    def make(cls, read: bool, write: bool, is_word: bool, indirect: bool, address_index: int):
        if address_index > cls.ADDRESS_INDEX_MASK:
            raise ValueError(f"Address index too large: Max {cls.ADDRESS_INDEX_MASK}, got {address_index}")
        if address_index < 0:
            raise ValueError(f"Address must be nonnegative, got {address_index}")
        self = cls(address_index)
        if read:
            self |= cls.HAS_READ
        if write:
            self |= cls.HAS_WRITE
        if is_word:
            self |= cls.IS_WORD
        if indirect:
            self |= cls.HAS_OFFSET
        return self


# No support for words
class NintendontOperation(NamedTuple):
    header: NintendontOperationHeader
    size: int
    indirect_offset: int | None
    data: bytes | None

    @classmethod
    def make_read(cls, address_index: int, size: int, indirect_offset: int | None = None):
        header = NintendontOperationHeader.make(True, False, False, indirect_offset is not None, address_index)
        return cls(header, size, indirect_offset, None)

    @classmethod
    def make_write(cls, read: int, address_index: int, data: bytes, indirect_offset: int | None = None):
        header = NintendontOperationHeader.make(read, True, False, indirect_offset is not None, address_index)
        return cls(header, len(data), indirect_offset, data)

    def is_read(self) -> bool:
        return NintendontOperationHeader.HAS_READ in self.header

    def to_bytes(self) -> bytes:
        if self.indirect_offset is None:
            data = struct.pack(">BB", self.header, self.size)
        else:
            data = struct.pack(">BBH", self.header, self.size, self.indirect_offset)
        if self.data is None:
            return data
        else:
            return data + self.data

class NintendontMetaInfo(NamedTuple):
    protocol_version: int
    max_input_bytes: int
    max_output_bytes: int
    max_addresses: int


class NintendontClient(GameCubeClient):
    address: str | None
    meta_info: NintendontMetaInfo | None
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    stream_lock: asyncio.Lock
    logger: Logger

    def __init__(self, logger: Logger):
        self.address = None
        self.meta_info = None
        self.reader = None
        self.writer = None
        self.stream_lock = asyncio.Lock()
        self.logger = logger

    def is_connected(self):
        return self.address is not None and self.reader is not None and self.writer is not None

    async def set_address(self, new_address: str | None):
        if new_address != self.address and self.is_connected():
            self.logger.info("Nintendont address changed, disconnecting.")
            await self.disconnect()
        self.address = new_address

    async def connect(self):
        if self.address is None:
            raise NintendontException("Address is not set")

        try:
            self.reader, self.writer = await asyncio.open_connection(self.address, NINTENDONT_PORT)
        except OSError as e:
            raise NintendontException from e

        try:
            data = struct.pack(">BBBB", NintendontMemoryOperationType.REQUEST_VERSION, 0, 0, True)
            result = await self.__write_to_socket(data)
            self.meta_info = NintendontMetaInfo._make(struct.unpack(">IIII", result))
            self.logger.debug(f"Protocol version: {self.meta_info.protocol_version}")
            self.logger.debug(f"Max input bytes: {self.meta_info.max_input_bytes}")
            self.logger.debug(f"Max output bytes: {self.meta_info.max_output_bytes}")
            self.logger.debug(f"Max addresses: {self.meta_info.max_addresses}")
        except:
            await self.disconnect()
            raise

    async def disconnect(self):
        try:
            if self.meta_info is not None:
                self.writer.close()
                await self.writer.wait_closed()
        except TimeoutError:
            pass
        self.reader = self.writer = self.meta_info = None

    async def __request_operations(self, addresses: list[int], memory_operations: list[NintendontOperation]) -> list[bytes | None]:
        if len(addresses) > self.meta_info.max_addresses:
            raise NintendontException(f"Too many addresses: Max is {self.meta_info.max_addresses}, got {len(addresses)}")

        data = bytearray()
        data.extend(struct.pack(">BBBB", NintendontMemoryOperationType.READ_COMMANDS, len(memory_operations), len(addresses), True))
        data.extend(itertools.chain.from_iterable(struct.pack(">I", address) for address in addresses))
        data.extend(itertools.chain.from_iterable(operation.to_bytes() for operation in memory_operations))
        if len(data) > self.meta_info.max_input_bytes:
            self.logger.warning(f"Command too long: {data.hex()}")
            raise NintendontException(f"Command too long: Max {self.meta_info.max_input_bytes} bytes, got {len(data)}")
        response = await self.__write_to_socket(data)

        results: list[bytes | None] = []
        current_index = ((len(memory_operations) - 1) // 8 + 1)
        success_bytes = response[:current_index]
        for i, op in enumerate(memory_operations):
            index = i // 8
            if success_bytes[index] & (1 << (i % 8)):
                if op.is_read():
                    result = response[current_index:current_index + op.size]
                    assert len(result) == op.size, f"Result: {result.hex()}, expected {op.size} bytes at index {current_index}"
                    results.append(result)
                    current_index += op.size
                else:
                    results.append(b'')
            else:
                results.append(None)
        return results

    async def __atomic_request(self, data: bytes | bytearray) -> bytes:
        try:
            await self.stream_lock.acquire()
            self.writer.write(data)
            await self.writer.drain()
            return await self.reader.read(1024)
        finally:
            self.stream_lock.release()

    async def __write_to_socket(self, data: bytes | bytearray) -> bytes:
        assert self.reader is not None and self.writer is not None
        try:
            response = await self.__atomic_request(data)
            if response == b'':
                await self.disconnect()
                raise NintendontException("Connection was closed")
            return response
        except OSError as e:
            await self.disconnect()
            raise NintendontException from e

    async def read_pointer(self, pointer: int, offset: int, byte_count: int) -> Any:
        return (await self.__request_operations([pointer], [NintendontOperation.make_read(0, byte_count, offset)]))[0]

    async def read_address(self, address: int, bytes_to_read: int) -> Any:
        result = (await self.__request_operations([address], [NintendontOperation.make_read(0, bytes_to_read)]))[0]
        if result == None:
            raise NintendontException(f"{address:x} -> {address + bytes_to_read:x} is not a valid for GC memory")
        return result

    # TODO: Find out what dolphin memory engine write_bytes() returns to match DolphinClient behavior. Currently assumed
    # to be the original value that was overwritten

    async def write_pointer(self, pointer: int, offset: int, data: Any):
        return (await self.__request_operations([pointer], [NintendontOperation.make_write(True, 0, cast(bytes, data), offset)]))[0]

    async def write_address(self, address: int, data: Any):
        # FIXME: Only read_address() raises on bad address. NintendontClient has the same asymmetry to maintain the same
        # behavior as DolphinClient
        return (await self.__request_operations([address], [NintendontOperation.make_write(True, 0, cast(bytes, data))]))[0]
