from __future__ import annotations
import typing
from construct.core import Construct

from construct.lib.containers import Container
from retro_data_structures.game_check import Game

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_provider import AssetProvider

AssetType = str
AssetId = int

class FormatWrapper:
    _raw: Container
    _asset_id: AssetId = None
    target_game: Game
    asset_provider: AssetProvider

    def __init__(self, raw: Container, target_game: Game, asset_provider: AssetProvider):
        self._raw = raw
        self.target_game = target_game
        self.asset_provider = asset_provider
    
    def get_asset(self, asset_id: AssetId) -> Container:
        with self.asset_provider as provider:
            return provider.get_asset(asset_id)
    
    @classmethod
    def from_asset(cls, asset_id: AssetId, target_game: Game, asset_provider: AssetProvider, *args) -> "FormatWrapper":
        with asset_provider as provider:
            raw = provider.get_asset(asset_id)
        wrapper = cls(raw, target_game, asset_provider, *args)
        wrapper._asset_id = asset_id
    
    @classmethod
    def construct_class(cls) -> Construct:
        raise NotImplementedError()

    @property
    def _built_raw(self) -> bytes:
        return self.construct_class().build(self._raw, target_game=self.target_game)
    
    @property
    def asset_id(self) -> AssetId:
        if self._asset_id is not None:
            return self._asset_id
        raise ValueError("No asset ID has been assigned.")
    
    @asset_id.setter
    def asset_id(self, value):
        self._asset_id = value
    
    def save_asset(self):
        with self.asset_provider as provider:
            provider.save_asset(self.asset_id, self._built_raw)
    