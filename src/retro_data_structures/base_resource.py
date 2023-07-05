from __future__ import annotations

import logging
import typing
import uuid

from construct import Construct, Container
from typing_extensions import Self

from retro_data_structures.exceptions import DependenciesHandledElsewhere

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.game_check import Game

AssetType = str
AssetId = int | uuid.UUID
NameOrAssetId = str | AssetId


class Dependency(typing.NamedTuple):
    type: AssetType
    id: AssetId
    exclude_for_mlvl: bool = False
    can_duplicate: bool = False

    def __repr__(self):
        s = f"Dep {self.type} 0x{self.id:08X}"
        if self.exclude_for_mlvl:
            s += " (non-MLVL)"
        return s


class BaseResource:
    _raw: Container
    target_game: Game
    asset_manager: AssetManager

    def __init__(self, raw: Container, target_game: Game, asset_manager: AssetManager | None = None):
        self._raw = raw
        self.target_game = target_game
        self.asset_manager = asset_manager

    @classmethod
    def construct_class(cls, target_game: Game) -> Construct:
        raise NotImplementedError()

    @classmethod
    def resource_type(cls) -> AssetType:
        raise NotImplementedError()

    @classmethod
    def parse(cls, data: bytes, target_game: Game,
              asset_manager: AssetManager | None = None) -> Self:
        return cls(cls.construct_class(target_game).parse(data, target_game=target_game),
                   target_game, asset_manager)

    def build(self) -> bytes:
        return self.construct_class(self.target_game).build(self._raw, target_game=self.target_game)

    @classmethod
    def has_dependencies(cls, target_game: Game) -> bool:
        dummy = cls(Container(), target_game, None)
        try:
            for _ in dummy.dependencies_for():
                return True
            return False

        except (KeyError, AttributeError):
            return True

        except DependenciesHandledElsewhere:
            return False

        except NotImplementedError:
            logging.warning("Potential missing dependencies for %s", cls.resource_type())
            return False

    def dependencies_for(self) -> typing.Iterator[Dependency]:
        raise NotImplementedError()

    @property
    def raw(self) -> Container:
        return self._raw


def resolve_asset_id(game: Game, value: NameOrAssetId) -> AssetId:
    if isinstance(value, str):
        value = game.hash_asset_id(value)

    if game.uses_guid_as_asset_id and isinstance(value, int):
        return uuid.UUID(int=value)

    return value


class RawResource(typing.NamedTuple):
    type: AssetType
    data: bytes
    compressed: bool = False

Resource = RawResource | BaseResource
