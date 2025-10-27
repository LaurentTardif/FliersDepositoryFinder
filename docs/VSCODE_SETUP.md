# 🔧 Guide VS Code pour FliersDepositoryFinder

## 📋 Vues et panneaux à ouvrir dans VS Code

### 1. 🧪 **Panel des Tests** (INDISPENSABLE)

```
Ctrl+Shift+P → "Python: Configure Tests" → unittest → tests folder → test_*.py
```

Puis ouvrir la vue Tests : `Ctrl+Shift+P → "Test: Focus on Test Explorer View"`

### 2. ⚡ **Panel des Tâches** (RECOMMANDÉ)

```
Ctrl+Shift+P → "Tasks: Run Task"
```

Tâches disponibles :

- 🧪 Lancer tous les tests
- 🔍 Vérifier la qualité du code
- 🎨 Formater le code automatiquement
- 📋 Tests par module (Filters, maj_historique, etc.)
- 🔧 Outils individuels (flake8, black, isort, mypy)

### 3. 🐛 **Panel de Debug** (OPTIONNEL)

```
Ctrl+Shift+D ou F5
```

Configurations disponibles :

- Debug tests
- Debug scripts individuels
- Debug avec arguments personnalisés

### 4. 🔍 **Panel des Problèmes** (AUTOMATIQUE)

```
Ctrl+Shift+M
```

Affiche automatiquement :

- Erreurs de syntaxe
- Warnings flake8
- Erreurs mypy
- Problèmes de formatage

### 5. 📁 **Explorateur de fichiers** (PAR DÉFAUT)

```
Ctrl+Shift+E
```

## 🚀 Comment exécuter les outils Python dans VS Code

### Option 1 : **Palette de commandes** (Le plus simple)

```
Ctrl+Shift+P → "Tasks: Run Task" → Choisir la tâche
```

### Option 2 : **Menu Terminal**

```
Terminal → Run Task → Choisir la tâche
```

### Option 3 : **Raccourcis claviers** (Configurables)

```
Ctrl+Shift+P → "Preferences: Open Keyboard Shortcuts"
```

Puis rechercher "Tasks: Run Task"

### Option 4 : **Via le terminal intégré**

```
Ctrl+` (backtick) puis taper directement :
python check_quality.py
python format_code.py
python tests/run_all_tests.py
```

### Option 5 : **Vue Tests intégrée**

```
Ctrl+Shift+P → "Test: Focus on Test Explorer View"
```

Clic sur ▶️ pour lancer les tests

## 🎯 Configuration automatique

Le projet configure automatiquement :

### ✅ **Formatage automatique**

- Sauvegarde → Black appliqué automatiquement
- Imports organisés avec isort
- Longueur de ligne : 127 caractères

### ✅ **Linting en temps réel**

- flake8 pour la syntaxe et le style
- mypy pour les types
- Problèmes affichés dans le panel "Problèmes"

### ✅ **Tests intégrés**

- Découverte automatique des 31 tests
- Exécution avec Ctrl+; ou via la vue Tests
- Résultats colorés dans l'éditeur

### ✅ **Environnement Python**

- Encodage UTF-8 configuré
- Environnement virtuel détecté automatiquement
- Chemins Python configurés

## 📊 Extensions recommandées

Le projet suggère automatiquement ces extensions :

### 🐍 **Python essentiels**

- `ms-python.python` - Support Python
- `ms-python.flake8` - Linting
- `ms-python.black-formatter` - Formatage
- `ms-python.isort` - Organisation imports
- `ms-python.mypy-type-checker` - Vérification types

### 🧪 **Tests**

- `ms-vscode.test-adapter-converter` - Adaptateur tests
- `littlefoxteam.vscode-python-test-adapter` - Tests Python

### 🔧 **Git**

- `eamodio.gitlens` - Git avancé
- `donjayamanne.githistory` - Historique Git

## 🔄 Workflow recommandé dans VS Code

### 1. **Développement**

```
1. Ouvrir un fichier Python
2. Modifier le code
3. Ctrl+S → Formatage automatique
4. Vérifier panel "Problèmes"
5. Corriger si nécessaire
```

### 2. **Tests**

```
1. Ctrl+Shift+P → "Test: Run All Tests"
   OU
2. Vue Tests → Clic sur ▶️
   OU
3. Ctrl+Shift+P → "Tasks: Run Task" → "🧪 Lancer tous les tests"
```

### 3. **Qualité**

```
1. Ctrl+Shift+P → "Tasks: Run Task" → "🔍 Vérifier la qualité du code"
   OU
2. Terminal → python check_quality.py
```

### 4. **Commit**

```
1. Ctrl+Shift+G → Vue Git
2. Stage changes
3. Commit message
4. Sync/Push
```

## 💡 Astuces VS Code

### **Raccourcis utiles**

- `Ctrl+Shift+P` : Palette de commandes
- `Ctrl+`` : Terminal intégré
- `Ctrl+Shift+M` : Panel Problèmes
- `Ctrl+Shift+E` : Explorateur
- `Ctrl+Shift+D` : Debug
- `F5` : Lancer debug
- `Ctrl+Shift+F5` : Relancer debug

### **Panel Terminal**

- Le terminal VS Code hérite de la configuration Python
- Encodage UTF-8 configuré automatiquement
- Environnement virtuel activé si présent

### **Personnalisation**

- Modifier `.vscode/settings.json` pour tes préférences
- Ajouter des raccourcis dans `.vscode/keybindings.json`
- Créer des tâches personnalisées dans `.vscode/tasks.json`

## 🚨 Résolution de problèmes

### **"Python introuvable"**

```
Ctrl+Shift+P → "Python: Select Interpreter"
```

### **"Module non trouvé"**

```
1. Vérifier l'environnement Python sélectionné
2. Installer : pip install -r requirements.txt
```

### **"Tests non découverts"**

```
Ctrl+Shift+P → "Python: Configure Tests" → unittest → tests/
```

### **"Formatage ne fonctionne pas"**

```
1. Installer Black : pip install black
2. Ctrl+Shift+P → "Python: Select Formatter" → black
```

Avec cette configuration, tu as accès à tous les outils Python directement dans VS Code ! 🎉
