
    //array of nodes
    var nodes = new vis.DataSet([
    ]);

    // create an array with edges
    var edges = new vis.DataSet([
    ]);

    // create a network
    var container = document.getElementById('mynetwork');

    // provide the data in the vis format
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        nodes: {
            fixed: {
                x:false,
                y:true
            },
        },
        edges: {
            smooth: {
                enabled: false,
                type: "dynamic",
                roundness: 0.5,
            },
        },
        layout: {
            randomSeed: undefined,
            improvedLayout:true,
            hierarchical: {
            enabled:true,
            direction: 'UD',        // UD, DU, LR, RL
            parentCentralization:true,
            sortMethod: 'directed'   // hubsize, directed
            }
        },
        physics: {
            enabled:false,


            hierarchicalRepulsion: {
            centralGravity: 0.0,
            springLength: 2000,
           springConstant: 0.01,
            nodeDistance: 1000,
            damping: 0.09
        },
      }
    };

    // initialize your network!
    var network = new vis.Network(container, data, options);