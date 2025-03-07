from __future__ import annotations
import typing
from typing import Optional, Union

from construct.core import (
    Const,
    Hex,
    If,
    IfThenElse,
    Int8ub,
    Int32ub,
    Peek,
    Pointer,
    Prefixed,
    PrefixedArray,
    Seek,
    Struct,
    Tell,
    this,
)
from construct.lib.containers import Container

from retro_data_structures import game_check
from retro_data_structures.common_types import FourCC
from retro_data_structures.construct_extensions.misc import Skip
from retro_data_structures.formats.script_object import ScriptInstance, ScriptInstanceHelper
from retro_data_structures.formats.wrapper import FormatWrapper
from retro_data_structures.game_check import Game

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_provider import AssetProvider
    from retro_data_structures.formats.mlvl import AreaHelper

ScriptLayerPrime = Struct(
    "magic" / Const("SCLY", FourCC),
    "unknown" / Int32ub,
    "_layer_count_address" / Tell,
    "_layer_count" / Peek(Int32ub),
    Skip(1, Int32ub),
    "_layer_size_address" / Tell,
    Seek(lambda this: (this._layer_count or len(this.layers)) * Int32ub.sizeof(), 1),
    "layers"
    / PrefixedArray(
        Pointer(this._._layer_count_address, Int32ub),
        Prefixed(
            Pointer(lambda this: this._._layer_size_address + this._index * Int32ub.sizeof(), Int32ub),
            Struct(
                "unk" / Hex(Int8ub),
                "objects" / PrefixedArray(Int32ub, ScriptInstance),
            ),
        ),
    ),
)


def ScriptLayer(identifier):
    return Struct(
        "magic" / Const(identifier, FourCC),
        "unknown" / Int8ub,
        "layer_index" / If(identifier == "SCLY", Int32ub),
        "version" / Const(1, Int8ub),
        "script_instances" / PrefixedArray(Int32ub, ScriptInstance),
    )

def new_layer(index: Optional[int], target_game: Game) -> Container:
    if target_game <= Game.PRIME:
        raise NotImplementedError()
    return Container({
        "magic": "SCLY" if index is not None else "SCGN",
        "unknown": 0,
        "layer_index": index,
        "version": 1,
        "script_instances": []
    })

SCLY = IfThenElse(game_check.current_game_at_least(game_check.Game.ECHOES), ScriptLayer("SCLY"), ScriptLayerPrime)
SCGN = ScriptLayer("SCGN")


class ScriptLayerHelper(FormatWrapper):
    _parent_area: Optional[AreaHelper] = None
    _index: Optional[int] = None

    def __repr__(self) -> str:
        if self.has_parent:
            return f"{self.name} ({'Active' if self.active else 'Inactive'})"
        return super().__repr__()

    @classmethod
    def with_parent(cls, child: "ScriptLayerHelper", parent: AreaHelper, index: int):
        new = cls(child._raw, child.target_game, child.asset_provider)
        new._parent_area = parent
        new._index = index
        return new
    
    @property
    def instances(self):
        for instance in self._raw.script_instances:
            yield ScriptInstanceHelper(instance, self.target_game, self.asset_provider)

    def get_instance(self, instance_id: int) -> Optional[ScriptInstanceHelper]:
        for instance in self.instances:
            if instance.id == instance_id:
                return instance

    def get_instance_by_name(self, name: str) -> ScriptInstanceHelper:
        for instance in self.instances:
            if instance.name == name:
                return instance
    
    def add_instance(self, instance_type: str, name: Optional[str] = None) -> ScriptInstanceHelper:
        instance = ScriptInstanceHelper.new_instance(self.target_game, instance_type, self)
        if name is not None:
            instance.name = name
        self._raw.script_instances.append(instance._raw)
        return self.get_instance(instance.id)
    
    def remove_instance(self, instance_id: int):
        self._raw.script_instances = [
            i for i in self._raw.script_instances
            if i.id.raw != instance_id
        ]

    def remove_instances(self):
        self._raw.script_instances = []

    def assert_parent(self):
        if self.has_parent:
            return
        if self._parent_area is None:
            raise AttributeError(f"{self} has no parent!")
        if self._index is None:
            raise AttributeError(f"{self} has no index!")
    
    @property
    def has_parent(self) -> bool:
        return self._parent_area is not None and self._index is not None

    @property
    def active(self) -> bool:
        self.assert_parent()
        return self._parent_area._flags[self._index]
    
    @active.setter
    def active(self, value: bool):
        self.assert_parent()
        self._parent_area._flags[self._index] = value
    
    @property
    def name(self) -> str:
        self.assert_parent()
        return self._parent_area._layer_names[self._index]
    
    @name.setter
    def name(self, value: str):
        self.assert_parent()
        self._parent_area._layer_names[self._index] = value
