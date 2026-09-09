@echo off
REM Script de build pour créer l'exécutable autonome GestionStock (Windows)
REM Ce script doit être exécuté depuis le dossier backend\

echo 🔨 Début du build de GestionStock...

REM Vérifier que PyInstaller est installé
where pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PyInstaller n'est pas installé. Installation en cours...
    pip install pyinstaller
)

REM Vérifier le chemin du projet
set PROJECT_PATH=%CD%
echo %PROJECT_PATH% | findstr /C:" " >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  ATTENTION: Le chemin du projet contient des espaces: %PROJECT_PATH%
    echo ⚠️  PyInstaller peut avoir des problèmes avec les chemins contenant des espaces.
    echo ⚠️  Il est recommandé de renommer le dossier pour supprimer les espaces.
    set /p CONTINUE="Continuer quand même? (y/N): "
    if /i not "%CONTINUE%"=="y" (
        echo ❌ Build annulé.
        exit /b 1
    )
)

echo %PROJECT_PATH% | findstr /C:"(" >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  ATTENTION: Le chemin du projet contient des parenthèses: %PROJECT_PATH%
    echo ⚠️  PyInstaller peut avoir des problèmes avec les parenthèses dans les chemins.
    echo ⚠️  Il est recommandé de renommer le dossier pour supprimer les parenthèses.
    set /p CONTINUE="Continuer quand même? (y/N): "
    if /i not "%CONTINUE%"=="y" (
        echo ❌ Build annulé.
        exit /b 1
    )
)

echo ✅ Vérifications terminées. Lancement du build...

REM Lancer PyInstaller avec le fichier .spec
pyinstaller --clean gestion_stock.spec

if %ERRORLEVEL% EQU 0 (
    echo ✅ Build terminé avec succès!
    echo 📦 L'exécutable se trouve dans: dist\GestionStock.exe
    echo.
    echo 📝 Pour tester l'exécutable:
    echo    cd dist
    echo    GestionStock.exe
    echo.
    echo 🗄️  La base de données sera créée à côté de l'exécutable (gestion_stock.db)
) else (
    echo ❌ Build échoué.
    exit /b 1
)