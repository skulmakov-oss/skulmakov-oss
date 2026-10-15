import hashlib, json, pathlib, zipfile
root = pathlib.Path(__file__).resolve().parent
manifest = json.loads((root / "INTEGRITY.json").read_text(encoding="utf-8"))
def digest(data):
    return hashlib.sha256(data).hexdigest()
expected = {x["path"] for x in manifest["files"]}
actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.name != "INTEGRITY.json"}
assert actual == expected, (actual - expected, expected - actual)
for entry in manifest["files"]:
    data = (root / entry["path"]).read_bytes()
    assert len(data) == entry["bytes"] and digest(data) == entry["sha256"], entry["path"]
with zipfile.ZipFile(root / "raw-records.zip") as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(set(archive.namelist()))
    entries = {x["path"]: x for x in manifest["zip_members"]}
    assert set(archive.namelist()) == set(entries)
    for name, entry in entries.items():
        assert not name.startswith("/") and ".." not in pathlib.PurePosixPath(name).parts
        data = archive.read(name)
        assert len(data) == entry["bytes"] and digest(data) == entry["sha256"], name
    for source in json.loads((root / "source-map.json").read_text(encoding="utf-8")):
        target = source["public_location"]
        data = archive.read(target.split("!", 1)[1]) if target.startswith("raw-records.zip!") else (root / target).read_bytes()
        assert digest(data) == source["public_sha256"], source["source"]
        if source["sanitization"] == "none; byte-identical":
            assert digest(data) == source["original_sha256"]
print("PASS: public files, package members, original/derivative mapping and duplicate references")
