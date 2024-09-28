#    <one line to give the program's name and a brief idea of what it does.>  
#    Copyright © 2024 Charudatta
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    email contact: 152109007c@gmailcom

set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

default:
    @just --choose

# create files and directories
init:
    #!pwsh
    git init
    New-Item -ItemType "file" -Path ".env", ".gitattribute", "run.py", "requirements.txt"
    New-Item -ItemType "directory" -Path "docs", "src", "tests"
    gig gen python > .gitignore 
    Add-LicenseHeader
    7z a archives.7z .gitignore

# add documentation to repo
docs:
    #!pwsh
    conda activate blog
    python -m mkdocs new .

# genearte and readme to repo    
readme:
    #!pwsh
    conda activate w
    python C:/Users/$env:username/Documents/GitHub/readmeGen/main.py

# version control repo with git
commit message="init":
    #!pwsh
    git add .
    git commit -m {{message}}

# create windows executable
exe file_name:
    #!pwsh
    pyinstaller src/{{file_name}} --onefile

# run python unit test 
tests:
    #!pwsh
    conda activate webdev
    python -m unittest discover -s tests

# run project
run:
    #!pwsh
    conda activate webdev
    start python run.py 
    set-Location src
    start nginx

# exit just file
quit:
    #!pwsh
    write-Host "Copyright © 2024 Charudatta"
    Write-Host "email contact: 152109007c@gmailcom"
    Write-Host "Exiting Folder" 
    [System.IO.Path]::GetFileName($(Get-Location))

# Add custom tasks, enviroment variables





        