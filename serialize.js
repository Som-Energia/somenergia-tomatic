var $tt = {};
var $headersText = [];
var $headersDays = $("th").slice(0,5);
var $headersHours = $("tbody th");
var $indexToDay2 = {0:'dl', 1:'dm', 2:'dx', 3:'dj', 4:'dv'}
$tt['timetable']={}
$headersDays.each(function(dayIndex){
    $tt['timetable'][$($headersDays[dayIndex]).text()]={}
  $headersHours.each(function(hoursIndex){
    $tt['timetable'][$($headersDays[dayIndex]).text()][hoursIndex+1]=[];
    });
  });
$cells = $($("tbody tr")).find("td:not(:contains(\xa0))");
      $cells.each(function(cellIndex){
        day=$indexToDay2[Math.floor(Math.floor(cellIndex%15)/3)];
        hour=Math.floor(cellIndex/15)+1;
        turn=Math.floor(cellIndex%3);
        $tt['timetable'][day][hour][turn]=$(this).text();
    });


alert(JSON.stringify($tt));
