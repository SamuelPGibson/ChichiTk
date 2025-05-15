# PYPI Upload

Install `build` in the current environment:

```bash
python -m pip install build
```

Build

```bash
python -m build
```

Install twine

```bash
python -m pip install twine
```

Upload

```bash
python -m twine upload dist/*
```

## License Issue

Go to `dist` folder and make sure the license file exists:

```bash
tar -tf .\chichitk-0.0.6.tar.gz
```

Fixed with new virtual environment!
