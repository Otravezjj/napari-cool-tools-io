@echo off
call conda --version
call conda activate napari-pytorch-dev-env
call napari --version
call napari
REM pause