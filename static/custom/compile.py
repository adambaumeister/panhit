import sass
import os
CUSTOM_SCSS = "scss" + os.path.sep + "custom.scss"
OUT = "compiled" + os.path.sep + "bootstrap.custom.css"

r = sass.compile(dirname=("scss", "compiled"))
