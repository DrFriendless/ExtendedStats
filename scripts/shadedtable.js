addEvent(window, "load", shadedtable_init);

function shadedtable_init() {
    // Find all tables with class greenbar and make them greenbar
    if (!document.getElementsByTagName) return;
    tbls = document.getElementsByTagName("table");
    for (ti=0;ti<tbls.length;ti++) {
		if (hasClassName(tbls[ti], "shaded")) makeShaded(tbls[ti]);
    }
}

function makeShaded(table) {
	if (!table) return;
	var trs = table.tBodies[0].rows;
	for (var i = 0; i < trs.length; i++) {
        removeClassName(trs[i], "even");
    }
	for (var i = 0; i < trs.length; i += 2) {
        addClassName(trs[i], "even");
    }
}


