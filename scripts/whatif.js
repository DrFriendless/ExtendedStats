if(HTMLElement){
    HTMLElement.prototype.__defineGetter__("innerText", function(){
        return this.textContent;
    });
    HTMLElement.prototype.__defineSetter__("innerText", function(v){
        this.textContent = v;
    });
}

lambda = Math.log(0.1) / -10.0;

addEvent(window, "load", whatif_init);

function makePlayable(td) {
    addEvent(td, "click", function() { inc(td); calc_cfm(); });
}

function makeClearable(td) {
    addEvent(td, "click", function() { clear(td); calc_cfm(); });
}

function makeOwnable(td) {
    addEvent(td, "click", function() { toggle(td); calc_cfm(); });
}

function cdf(x) {
    return 1.0 - Math.exp(-lambda * x)
}

function invcdf(x) {
    return -Math.log(1.0 - x) / lambda
}

function whatif_init() {
    // Find all tables with class sortable and make them sortable
    if (!document.getElementsByTagName) return;
    tds = document.getElementsByTagName("td");
    p = 0; q= 0;
    for (ti=0;ti<tds.length;ti++) {
        td = tds[ti];
        if ( hasClassName( td, "hplays" )) {
            makePlayable(td);
        }
        if ( hasClassName( td, "clear" )) {
            makeClearable(td);
        }
        if ( hasClassName( td, "hown" )) {
            makeOwnable(td);
        }
    }
    calc_cfm();
}

function inc(td) {
    td.innerText = "" + (parseInt(ts_getInnerText(td)) + 1);
    td.parentNode.getElementsByTagName("td")[5].innerText = "Yes";
}

function toggle(td) {
    var txt = ts_getInnerText(td);
    if (txt == "Yes") {
        txt = "No";
    } else {
        txt = "Yes";
    }
    td.innerText = txt;
    td.parentNode.getElementsByTagName("td")[5].innerText = "Yes";
}

function clear(td) {
    row = td.parentNode;
    var tds = row.getElementsByTagName("td");
    tds[3].innerText = tds[1].innerText;
    tds[4].innerText = tds[2].innerText;
    tds[5].innerText = "";
}

function calc_cfm() {
    table = document.getElementById("whatiftab");
    var rows = table.getElementsByTagName("tr");
    var tot = 0.0;
    var rtot = 0.0;
    var count = 0.0;
    var rcount = 0.0;
    for (r=0; r<rows.length; r++) {
        var tds = rows[r].getElementsByTagName("td");
        if (tds[2].innerText  == "Yes") {
            var plays = parseInt(ts_getInnerText(tds[1]));
            if (!plays.isNan) {
                rtot = rtot + cdf(plays);
                rcount = rcount + 1.0;
            }
        }
        if (tds[4].innerText == "Yes") {
            var plays = parseInt(ts_getInnerText(tds[3]));
            if (!plays.isNan) {
                tot = tot + cdf(plays);
                count = count + 1.0;
            }
        }
    }
    var util = 0.0;
    if (count > 0.0) util = tot / count;
    var cfm = invcdf(util);
    var rutil = 0.0;
    if (rcount > 0.0) rutil = rtot / rcount;
    var rcfm = invcdf(rutil);
    document.getElementById("cfm").innerText = "Real CFM = " + (Math.round(rcfm * 100) / 100.0);
    document.getElementById("util").innerText = "Real Utilisation = " + (Math.round(rutil * 10000) / 100.0) + "%";
    document.getElementById("hcfm").innerText = "Hypothetical CFM = " + (Math.round(cfm * 100) / 100.0);
    document.getElementById("hutil").innerText = "Hypothetical Utilisation = " + (Math.round(util * 10000) / 100.0) + "%";
}
