var $tt = {};
var $headersText = [];
var $headersDays = $("th").slice(0,5);
var $headersHours = $("tbody th");
var $indexToDay = {0:'dl', 1:'dl', 2:'dl', 3:'dm',4:'dm',5:'dm', 6:'dx',7:'dx',8:'dx', 9:'dj', 10:'dj', 11:'dj', 12:'dv', 13:'dv',14:'dv'};
$tt['timetable']={}
$headersDays.each(function(dayIndex){
	$tt['timetable'][$($headersDays[dayIndex]).text()]={}
  $headersHours.each(function(hoursIndex){
  	$tt['timetable'][$($headersDays[dayIndex]).text()][hoursIndex+1]=[];
    });
  });
$cells = $($("tbody tr")).find("td:not(:contains(\xa0))");
      $cells.each(function(cellIndex){
        day=$indexToDay[Math.floor(cellIndex%15)];
        hour=Math.floor(cellIndex/15)+1;
        turn=Math.floor(cellIndex%3);
        $tt['timetable'][day][hour][turn]=$(this).text();
    });
