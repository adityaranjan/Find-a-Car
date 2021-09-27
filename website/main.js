document.getElementById("loadingDiv").style.display = "none";
document.getElementById("outputDiv").style.display = "none";

function apiPost()
{
	var xhr = new XMLHttpRequest();
	var url = "AWS_API_GOES_HERE";
			
	xhr.open("POST", url, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	
	document.getElementById("inputDiv").style.display = "none";
	document.getElementById("loadingDiv").style.display = "block";
	document.getElementById("loadingImg").innerHTML = '<img src= "images/loading.gif" width = "100" height = "100" />'
	
	xhr.onreadystatechange = function ()
	{
    	if (xhr.readyState == XMLHttpRequest.DONE)
    	{
    		var outputJson = JSON.parse(xhr.responseText);
    		
    		document.getElementById("loadingDiv").style.display = "none";
    	    document.getElementById("outputDiv").style.display = "block";
    	
    		for (i = 0; i < 5; i++)
    		{
        		document.getElementById("carnames".concat((i + 1).toString(10))).innerHTML = ((i + 1).toString(10)).concat(") ", outputJson.names[i]);
        		document.getElementById("carscores".concat((i + 1).toString(10))).innerHTML = outputJson.scores[i];
			}
    	}
	};
			
	var maxPrice = document.getElementById("priceSliderID").value;
			
	var checkboxIDS = ["householdSizeID", "dailyCommuteID", "ecoFriendlyID", "luxuryChoiceID"];
	var checkboxInputs = [];
	for (id of checkboxIDS)
	{
		if (document.getElementById(id).checked == true)
		{
			checkboxInputs.push("Y");
		}
		else
		{
			checkboxInputs.push("N");
		}
	}
			
	var data = JSON.stringify({"maxPrice": maxPrice, "householdSize": checkboxInputs[0], "dailyCommute": checkboxInputs[1], "ecoFriendly": checkboxInputs[2], "luxuryChoice": checkboxInputs[3]});
	xhr.send(data);
};