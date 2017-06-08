Alquist Editor
=======

Alquist Editor provides a quick way to see the structure of dialogues created for Alquist dialogue manager and edit their code at the same time.

It consists of a javascript client that displays graph of dialogue's states and contains a simple user interface and python server which generates graph nodes and edges from yaml codes and provides basic file management. 

Editor can be accesed on /editor/ url, for example http://127.0.0.1:5000/editor/

###Used javascript libraries
**Viz.js** https://github.com/mdaines/viz.js/  - used for displaying graph of dialogue states 

**JQuery** https://jquery.com

**SVG Pan Zoom** https://github.com/ariutta/svg-pan-zoom - enables easy panning and zooming of graph

**Split.js** https://nathancahill.github.io/Split.js/ - enables splitting web page into several panes

**Tab Override** https://github.com/wjbryant/taboverride - enables use of tab key in text area (default size of 2 spaces)

**CodeMirror** https://codemirror.net - enables syntax highlighting, autoindent, line numbers...

**jsTree** https://www.jstree.com - jquery plugin which provides interactive trees (displays interactive file structure)

**jsTree Proton theme** https://github.com/orangehill/jstree-bootstrap-theme - theme for jsTree plugin

**Bootstrap** http://getbootstrap.com - javascript framework

**Bootbox** http://bootboxjs.com - provides programmatic dialogue boxes for Bootstrap
    <script src="../static-files/bootbox.min.js"></script>