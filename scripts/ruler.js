/*==========================================
  Ruler
==========================================*/
addEvent(window, "load", ruler_init);

function ruler_init() {
    // Find all tables with class greenbar and make them ruler
    if (!document.getElementsByTagName) return;
    tbls = document.getElementsByTagName("table");
    for (ti=0;ti<tbls.length;ti++) {
		if (hasClassName(tbls[ti], "ruler")) makeRuler(tbls[ti]);
    }
}

function makeRuler(table) {
	var trs=table.getElementsByTagName('tr');
	for(var j=0;j<trs.length;j++) {
		if(trs[j].parentNode.nodeName=='TBODY' && !hasClassName( trs[j], "sectionheader" )) {
			trs[j].onmouseover=function(){
				this.className = this.className.replace( 'ruled', "" ).trim();
				this.className = ( this.className + " ruled" ).trim();
				return false
			}
			trs[j].onmouseout=function(){
				this.className = this.className.replace( 'ruled', "" ).trim();
				return false
			}
			
		}
	}
}
