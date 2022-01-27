from pathlib import Path
import pytest
from retro_data_structures.asset_provider import AssetProvider
from retro_data_structures.formats.mlvl import MLVL, Mlvl
from retro_data_structures.game_check import Game
from test.test_lib import parse_and_build_compare


areas_of_interest = {
    0x3A9B7C8D: 0x3A9B7C8D,
    0x3B696A7A: 0x3B696A7A,
    0x57E7BDCA: 0x57E7BDCA,
    0x469F86A0: 0x469F86A0,
    0x57E7BDCA: 0x57E7BDCA,
    0x628F4FC2: 0x628F4FC2,
    0x7D231C5D: 0x7D231C5D,
    0x80CBA3E1: -0x7F345C1F,
    0x8E2AF917: -0x71D506E9,
    0x9A2ACAFD: -0x65D53503,
    0xA1E4608C: -0x5E1B9F74,
    0xA9FB8A2B: -0x560475D5,
    0xBA47CB1F: -0x45B834E1,
    0xAF3C03B1: -0x50C3FC4F,
    0xC1AE6ECF: -0x3E519131,
    0xE13DA78B: -0x1EC25875,
    0xDC8B67D3: -0x2374982D,
    0xE250F791: -0x1DAF086F,
    0xE380B5A7: -0x1C7F4A59,
    0xE5F82542: -0x1A07DABE,
    0xEF855B84: -0x107AA47C,
    0xFB3385B5: -0x4CC7A4B,
    0xEAA44A69: -0x155BB597,
    0x416E3BA9: 0x416E3BA9,
}

@pytest.mark.parametrize("path", [
        "Worlds/SandWorld/!SandWorld_Master/!SandWorld_Master.MLVL",
        "Worlds/CliffWorld/!CliffWorld_Master/!CliffWorld_Master.MLVL",
        "Worlds/SwampWorld/!SwampWorld_Master/!SwampWorld_Master.MLVL",
        "Worlds/TempleHub/!TempleHub_Master/!TempleHub_Master.MLVL",
        "Worlds/TempleInt/!TempleInt_Master/!TempleInt_Master.MLVL"
    ])
# @pytest.mark.skip
def test_compare_p2(prime2_pwe_project, prime2_paks_path: Path, path):
    data = MLVL.parse(prime2_pwe_project.joinpath("Resources").joinpath(path).read_bytes(), target_game=Game.ECHOES)
    paks = [pak for pak in prime2_paks_path.glob("*.pak")]
    mlvl = Mlvl(data, Game.ECHOES, AssetProvider(Game.ECHOES, paks))
    print()
    print(mlvl)
    for a in mlvl.areas:
        if a.id not in areas_of_interest.keys():
            continue
        print(f"{a.name}: {hex(areas_of_interest[a.id])}")
    