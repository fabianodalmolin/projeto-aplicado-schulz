@echo off
echo Verificando e instalando PyInstaller...
python -m pip install pyinstaller

echo Gerando o executavel Schulz_Calibracao.exe...
python -m PyInstaller --onefile --windowed --name "Schulz_Calibracao" gerador_certificado_07.py

echo Processo finalizado! O executavel esta na pasta dist.
pause
