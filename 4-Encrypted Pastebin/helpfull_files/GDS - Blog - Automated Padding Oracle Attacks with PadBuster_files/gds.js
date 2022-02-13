// JavaScript Document
// Function to remove white spaces from nodes


function mainNav(mainNavID, subNavID, height)
{
	var mainNavID = $(mainNavID);
	var subNavID = $(subNavID);
	var height = height +'px';
	
	var mainnavtimerOver = null;
	var mainnavtimerOut = null;
	var subnavtimer = null;
	var current = '';
	var subnavIson = false;
	
	var blindup = null;
	var blinddown = null;
	
	//methods
	this.init = init;
	this.hidesubnav = hidesubnav;
	this.showsubnav = showsubnav;
	this.subnavRover = subnavRover;
	this.subnavRout = subnavRout;
		
	function init()
	{
		mainNavID.onmouseover = function (e)
		{
			if (!e) var e = window.event;
			clearTimeout(subnavtimer);
			mainnavtimerOver = setTimeout(
				function () { showsubnav();  }
			,200);
		}		
		if (mainNavID.captureEvents) mainNavID.captureEvents(Event.ONMOUSEOVER);
		
		mainNavID.onmouseout = function (e)
		{
			if (!e) var e = window.event;
			clearTimeout(mainnavtimerOver);
			mainnavtimerOut = setTimeout(
				function () {hidesubnav(); }
			,200);
		}		
		if (mainNavID.captureEvents) mainNavID.captureEvents(Event.ONMOUSEOUT);

		mainNavID.onmouseover = function (e)
		{
			if (!e) var e = window.event;
			clearTimeout(subnavtimer);
			mainnavtimerOver = setTimeout(
				function () { showsubnav();  }
			,200);
		}		
		if (mainNavID.captureEvents) mainNavID.captureEvents(Event.ONMOUSEOVER);

		subNavID.onmouseover = function (e)
		{
			if (!e) var e = window.event;
			mainNavID.style.backgroundColor = '#223A63';
			mainNavID.style.color = '#FFFFFF';
			clearTimeout(mainnavtimerOut);
			clearTimeout(subnavtimer);
		}		
		if (subNavID.captureEvents) subNavID.captureEvents(Event.ONMOUSEOVER);

		subNavID.onmouseout = function (e)
		{
			if (!e) var e = window.event;
			mainNavID.style.backgroundColor = '';
			mainNavID.style.color = '';
			
			subnavtimer = setTimeout(
				function () {hidesubnav(); }
			,200);
		}		
		if (subNavID.captureEvents) subNavID.captureEvents(Event.ONMOUSEOUT);

		hidesubnav();
	}
	
	function subnavRover()
	{
		subnavIson = false;
	}
	function subnavRout()
	{
		subnavIson = true;
	}
	
	function hidesubnav()
	{
		subNavID.style.zIndex = '1';
		new Effect.BlindUp(subNavID, 
		{
			duration:0.2,
			afterFinish: function ()
			{
				subNavID.style.height = height;
				//subnavIson = false;
				//currentsubnav = '';
			}
		});		
	}
	
	function showsubnav()
	{
		if(!subnavIson)
		{
			subNavID.style.visibility = 'visible';
			subNavID.style.zIndex = '100';
			new Effect.BlindDown(subNavID, 
			{
				duration:0.2,
				afterFinish: function ()
				{
					//subnavIson = true;
					//currentsubnav = node.id;
				}
			});
		}	
	}
	
}


function initNav()
{
	var mainNavDiv = $('mainNav');
	var aNavs = mainNavDiv.getElementsByTagName('a');
	
	var navObjects = new Array(); 
	
	for(i=0; i<aNavs.length; i++)
	{
		var navID = aNavs[i].id;
		var subnavID = aNavs[i].id+'_submenu';
		var addnewnav = new mainNav(navID, subnavID, 200);
		navObjects.push(addnewnav);
	}
	
	for(i=0; i<navObjects.length; i++)
	{
			navObjects[i].init();
	}
}


/*
var timer = null;
var mainnavtimerOver = null;
var mainnavtimerOut = null;

var subnavtimer = null;
var subnavIson = false;
var currentsubnav = '';
var currentmainnav = '';

function removeWhitespace(node) 
{
	var loopIndex;
	
	for (loopIndex = 0; loopIndex < node.childNodes.length; 
	  loopIndex++) {
	
	  var currentNode = node.childNodes[loopIndex];
	
	  if (currentNode.nodeType == 1) {
		removeWhitespace(currentNode);
	  }
	
	  if (((/^\s+$/.test(currentNode.nodeValue))) &&   
		(currentNode.nodeType == 3)) {
		  node.removeChild(node.childNodes[loopIndex--]);
	  }
	}
}

function turnalloff()
{
	removeWhitespace($('subnavs')) 
	var subNavDivs = $('subnavs').childNodes;
		
	for(i=0; i< subNavDivs.length; i++)
		{
			subNavDivs[i].style.visibility = 'visible';
			new Effect.BlindUp(subNavDivs[i], 
			{
				duration:0.2
			});
		}	
	if(currentsubnav != '')
	{
		

		$(currentsubnav).style.visibility = 'visible';
			new Effect.BlindUp($(currentsubnav), 
			{
				duration:0.2
			});
	
	}
}	

function subnavRover()
{
	subnavIson = false;
}
function subnavRout()
{
	subnavIson = true;
}



function subnavon(node)
{
	//alert(node.style.visibility);
	if(!subnavIson)
	{
		node.style.visibility = 'visible';
		node.style.zIndex = '100';
		new Effect.BlindDown(node, 
		{
			duration:0.2,
			afterFinish: function ()
			{
				subnavIson = true;
				currentsubnav = node.id;
			}
		});
		
		
	}
	//new Effect.Appear(node, {duration:0.3});
}
function subnavoff(node)
{
	//alert(node.style.visibility);
	//if(subnavIson)
	//{
		node.style.zIndex = '1';
		new Effect.BlindUp(node, 
		{
			duration:0.2,
			afterFinish: function ()
			{
				subnavIson = false;
				currentsubnav = '';
			}
		});		
	//}
	//new Effect.Fade(node, {duration:0.2});
	
}

function initNav()
{
	var mainNavDiv = $('mainNav');
	var aNavs = mainNavDiv.getElementsByTagName('a');
	
	removeWhitespace($('subnavs')) 
	var subNavDivs = $('subnavs').childNodes;
	for(i = 0; i < subNavDivs.length; i++)
	{
		subNavDivs[i].style.visibility = 'hidden';
		subNavDivs[i].onmouseover = function (e)
		{
			
			if (!e) var e = window.event;
			//clearTimeout(timer);
			//clearTimeout(subnavtimer);
			var MainNavID = this.id.replace('_submenu','');
			var MainNavNode = $(MainNavID);	
			MainNavNode.style.backgroundColor = '#223A63';
			MainNavNode.style.color = '#FFFFFF';
			//subnavRover();
			//var subnav =  $(this.id);
			clearTimeout(mainnavtimerOut);
			clearTimeout(subnavtimer);
			//clearTimeout(mainnavtimerOver);
			setTimeout(
				function () {subnavon(subnav); }
			,500);
			
		}		
		if (subNavDivs[i].captureEvents) subNavDivs[i].captureEvents(Event.ONMOUSEOVER);
		
		subNavDivs[i].onmouseout = function (e)
		{
			if (!e) var e = window.event;
			var MainNavID = this.id.replace('_submenu','');
			var MainNavNode = $(MainNavID);
			MainNavNode.style.backgroundColor = '';
			MainNavNode.style.color = '';
				
			var subnav =  $(this.id);
			subnavtimer = setTimeout(
				function () {subnavoff(subnav); }
			,200);
			//alert(subnav);
			
			//subnavoff(subnav);
			//subnavRout();
			//setTimeout(
				//function () {subnavoff(subnav); }
			//,500);
			
		}		
		if (subNavDivs[i].captureEvents) subNavDivs[i].captureEvents(Event.ONMOUSEOUT);
	}
	
	
	//onmouseover="subnavon('submenu1')" onmouseout="subnavoff('submenu1')"
	
		
	// Init Main Nav
	
	for(i = 0; i < aNavs.length; i++)
	{
		
		aNavs[i].onmouseover = function (e)
		{
			if (!e) var e = window.event;
			
			currentmainnav = this.id + '_submenu';
			
			var subnavID = this.id +'_submenu';
			var subnav = $(subnavID);
			
			if(currentmainnav != currentsubnav)
			{
				
				setTimeout(
				function () {  }
			,200);
				//turnalloff();
				subnavIson = false;
			}
			
			//subnavon(subnav);
			clearTimeout(subnavtimer);
			mainnavtimerOver = setTimeout(
				function () {subnavon(subnav);  }
			,200);
			//clearTimeout(subnavtimer);
			if(subnav.style.visibility != 'visible')
			{
				turnalloff();
			timeron = setTimeout(
				function () {subnavon(subnav);  }
			,300);
			}
		}		
		if (aNavs[i].captureEvents) aNavs[i].captureEvents(Event.ONMOUSEOVER);
		
		aNavs[i].onmouseout = function (e)
		{
			if (!e) var e = window.event;
			//clearTimeout(timeron);
			var subnavID = this.id +'_submenu';
			var subnav = $(subnavID);
			
			//subnavoff(subnav);
			//clearTimeout(mainnavtimerOut);
			clearTimeout(mainnavtimerOver);
			mainnavtimerOut = setTimeout(
				function () {subnavoff(subnav); }
			,200);
			
			timer = setTimeout(
				function () {subnavoff(subnav); }
			,200);
		}		
		if (aNavs[i].captureEvents) aNavs[i].captureEvents(Event.ONMOUSEOUT);
		
	}
}
*/