/* Cookies Directive Disclosure Script
 * Version: 1.1
 * Author: Ollie Phillips
 * 17 March 2012 
 */


function cookiesDirective(disclosurePos,privacyPolicyUri, cookieScripts) {
	
	// From v1.1 the position can be set to 'top' or 'bottom' of viewport
	var disclosurePosition = disclosurePos;

	// Better check it!
	if((disclosurePosition.toLowerCase() != 'top') && (disclosurePosition.toLowerCase() != 'bottom')) {
		
		// Set a default of top
		disclosurePosition = 'top';
	
	}
	
	// Start Test/Loader (improved in v1.1)
	var jQueryVersion = '1.5';
	
	// Test for JQuery and load if not available
	if (window.jQuery === undefined || window.jQuery.fn.jquery < jQueryVersion) {
		
		var s = document.createElement("script");
		s.src = "https://ajax.googleapis.com/ajax/libs/jquery/" + jQueryVersion + "/jquery.min.js";
		s.type = "text/javascript";
		s.onload = s.onreadystatechange = function() {
		
			if ((!s.readyState || s.readyState == "loaded" || s.readyState == "complete")) {

                // Do not conflict with prototype and friends
                $j = jQuery.noConflict();
	
				// Safe to proceed	
				if(!cdReadCookie('cookiesDirective')) {
					
					// Cookies not accepted make disclosure
					if(cookieScripts) {
						
						cdHandler(disclosurePosition,privacyPolicyUri,cookieScripts);

					} else {
						
						cdHandler(disclosurePosition,privacyPolicyUri);

					}		
					
				} else {
					
					// Cookies accepted run script wrapper
					cookiesDirectiveScriptWrapper();
					
				}		
				
			}	
		
		}
	
		document.getElementsByTagName("head")[0].appendChild(s);		
	
	} else {
		
		// We have JQuery and right version
		if(!cdReadCookie('cookiesDirective')) {
			
			// Cookies not accepted make disclosure
			if(cookieScripts) {
				
				cdHandler(disclosurePosition,privacyPolicyUri,cookieScripts);

			} else {
				
				cdHandler(disclosurePosition,privacyPolicyUri);

			}		
			
		} else {
			
			// Cookies accepted run script wrapper
			cookiesDirectiveScriptWrapper();
			
		}
		
	}	
	// End Test/Loader
}


function cdHandler(disclosurePosition, privacyPolicyUri, cookieScripts) {
	
	// Our main disclosure script
	jQuery(document).ready(function(){

		var epdApps;
		var epdAppsCount;
		var epdAppsDisclosure;
		var epdPrivacyPolicyUri;
		var epdDisclosurePosition;
		
		epdDisclosurePosition = disclosurePosition;
		epdPrivacyPolicyUri = privacyPolicyUri;
		
		// What scripts must be declared, user passes these as comma delimited string
		if (cookieScripts) {
			
			epdApps = cookieScripts.split(',');
			epdAppsCount = epdApps.length;
			var epdAppsDisclosureText='';
			
			if(epdAppsCount>1) {
				
				for(var t=0; t < epdAppsCount - 1; t++) {
					
					epdAppsDisclosureText += epdApps[t] + ', ';	
								
				}	
				
				epdAppsDisclosure = ' We also use ' + epdAppsDisclosureText.substring(0, epdAppsDisclosureText.length - 2) + ' and ' + epdApps[epdAppsCount - 1] + ' scripts, which all use cookies. ';
			
			} else {
				
				epdAppsDisclosure = ' We also use a ' + epdApps[0] + ' script which uses cookies.';		
				
			}
				
		} else {
			
			epdAppsDisclosure = '';
			
		}
		
		// Create our overlay with message
		var divNode = document.createElement('div');
		divNode.setAttribute('id','epd');
		document.body.appendChild(divNode);
		
		// The disclosure narrative pretty much follows that on the Information Commissioners Office website		
		var disclosure = '<div id="cookiesdirective" style="position:fixed;'+ epdDisclosurePosition + ':-300px;left:0px;width:100%;height:auto;background:#000000;opacity:.80; -ms-filter: “alpha(opacity=80)”; filter: alpha(opacity=80);-khtml-opacity: .80; -moz-opacity: .80; color:#FFFFFF;font-family:arial;font-size:14px;text-align:center;z-index:1000;">';
		
		disclosure +='<div style="position:relative;height:auto;width:90%;padding:15px;margin-left:auto;margin-right:auto;">';	
		disclosure += 'This site uses cookies to improve your experience. ';
		disclosure += 'Continued use of this site indicates that you accept our ';
		disclosure += '<a href="https://www.strozfriedberg.com/privacy-policy/" target="_blank">privacy and cookie policy.</a>&nbsp;';
		disclosure += '<input type="submit" name="epdsubmit" id="epdsubmit" value="Accept"/><br/><br/></div></div>';
		document.getElementById("epd").innerHTML= disclosure;
	  	
		// Bring our overlay in
		if(epdDisclosurePosition.toLowerCase() == 'top') { 
		
			// Serve from top of page
			jQuery('#cookiesdirective').animate({
			    top: '0'
			 }, 1000, function() {
				// Overlay is displayed, set a listener on the button
				jQuery('#epdsubmit').click(function() {
			  
					if(document.getElementById('epdagree').checked){
						
						// Set a cookie to prevent this being displayed again
						cdCreateCookie('cookiesDirective',1,365);	
						// Close the overlay
						jQuery('#cookiesdirective').animate({
							top:'-300'
						},1000,function(){
							
							// Remove the elements from the DOM and reload page, which should now
							// fire our the scripts enclosed by our wrapper function
							jQuery('#cookiesdirective').remove();
							location.reload(true);
							
						});
						
					} else {
						
						// We need the box checked we want "explicit consent", display message
						document.getElementById('epdnotick').style.display = 'block';
							
					}
				});
			});
		
		} else {
		
			// Serve from bottom of page
			jQuery('#cookiesdirective').animate({
			    bottom: '0'
			 }, 1000, function() {
				
				// Overlay is displayed, set a listener on the button
				jQuery('#epdsubmit').click(function() {
			  
		//			if(document.getElementById('epdagree').checked) {
						 
						// Set a cookie to prevent this being displayed again
						cdCreateCookie('cookiesDirective',1,365);	
						// Close the overlay
						jQuery('#cookiesdirective').animate({
							bottom:'-300'
						},1000,function() { 
							
							// Remove the elements from the DOM and reload page, which should now
							// fire our the scripts enclosed by our wrapper function
							jQuery('#cookiesdirective').remove();
							location.reload(true);
							
						});
						
		//			} else {
						
						// We need the box checked we want "explicit consent", display message
		//				document.getElementById('epdnotick').style.display = 'block';	
						
		//			}
				});
			});
			
		}			
		
	});
		
}


function cdScriptAppend(scriptUri, myLocation) {
		
	// Reworked in Version 1.1 - needed a more robust loader

	var elementId = String(myLocation);
	var sA = document.createElement("script");
	sA.src = scriptUri;
	sA.type = "text/javascript";
	sA.onload = sA.onreadystatechange = function() {

		if ((!sA.readyState || sA.readyState == "loaded" || sA.readyState == "complete")) {
				
			return;
		
		} 	

	}

	switch(myLocation) {
		
		case 'head':
			document.getElementsByTagName('head')[0].appendChild(sA);
		  	break;
	
		case 'body':
			document.getElementsByTagName('body')[0].appendChild(sA);
		  	break;
	
		default: 
			document.getElementById(elementId).appendChild(sA);
			
	}	
		
}


// Simple Cookie functions from http://www.quirksmode.org/js/cookies.html - thanks!
function cdReadCookie(name) {
	
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	
	return null;
	
}

function cdCreateCookie(name,value,days) {
	
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
	
}
