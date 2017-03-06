// *************************************************************
// Tabellen
// *************************************************************

function draw_table(data, target) {

    //
    var table = $(target)

    // als er al een tabel is, deze leeg maken
    if (table.children('tbody').length > 0) {table.children('tbody').remove()};
    //
    // // body (opnieuw) toevoegen aan table
    var tbody = table.append($("<tbody id='prod_body'></tbody>"))
    //
    // //header regel
    var h_row = tbody.append($("<tr id='prod_header'></tr>"))
    h_row = $('#prod_header')
    //
    // // eerste cel in elke regel geeft aan wat er in die regel staat.
    // // header regel heeft daar lege cel
    h_row.append('<th></th>')
    //
    // // in de header regel komen de maanden te staan.
    // // lenen een stukje d3 om de datum in het formaat te krijgen
    var date_format = d3.time.format('%b %Y')
    //
    // // dan langs data lopen om de header regel te vullen met datums
    $.each(data.cumulatief[0].values, function(k, v){
      var text = new Date(v.x)
      var cell = h_row.append($('<th>' + date_format(text) + '</th>'))
    })
    //



    function row_add(add_to, d, id, klasse) {
      // id en class is nodig voor de functie, maar niet per se noodzakelijk voor
      // gebruiker. Dus als niet opgegegen, dan random
      if(typeof(id)==='undefined') {var id = ('id_' + new Date().getTime())};
      if(typeof(klasse)==='undefined') {var klasse = 'class_' + new Date().getTime();}

      // rij toevoegen, id is nodig om rij weer te selecteren
      add_to = add_to.append($('<tr id=' + id + '>' + '</tr>'))

      //rij selecteren obv id en class zetten
      var row = $(('#' + id)).attr('class', klasse)

      // eerste cel in elke regel geeft aan wat er in die regel staat.
      row.append('<td>' + d.key + '</td>')

      // dan de rest door over data heen te loopen
      $.each(d.values, function(k, v){
        var cell = row.append($('<td>' + v.y + '</td>'))
      })
    };

    // regel voor beschikbare uren
    row_add(add_to = $('#prod_body'), d = data.data[0], id = 'beschikbaar', klasse = 'beschikbaar')
    // regel voor gerealiseerde uren
    row_add(add_to = $('#prod_body'), data = data.data[1], id = 'gerealiseerd', klasse = 'gerealiseerd')

};


// *************************************************************
// NVD3 Grafieken
//**************************************************************

function bar(data, target_id) {

  var chart;
  nv.addGraph(function() {
      chart = nv.models.multiBarChart()
          .duration(300)
          .margin({bottom: 100, left: 70})
          .rotateLabels(-45)
          .groupSpacing(0.1)
          .showControls(false)
      ;
      chart.reduceXTicks(false).staggerLabels(true);
      chart.xAxis
          .axisLabel("datum")
          .axisLabelDistance(35)
          .showMaxMin(false)
          .tickFormat(function(d) {
                      return d3.time.format('%b-%y')(new Date(d))
                  });
      ;
      chart.yAxis
          .axisLabel("uren")
          .axisLabelDistance(-5)
          .tickFormat(d3.format('.'))
      ;
      chart.dispatch.on('renderEnd', function(){
          nv.log('Render Complete');
      });
      d3.select(target_id)
          .datum(data)
          .call(chart);


      nv.utils.windowResize(chart.update);
      chart.dispatch.on('stateChange', function(e) {
          nv.log('New State:', JSON.stringify(e));
      });
      chart.state.dispatch.on('change', function(state){
          nv.log('state', JSON.stringify(state));
      });
      return chart;
  });
}


function line(data, target_id) {

    var chart;
    nv.addGraph(function() {
        chart = nv.models.lineChart()
            .options({
                duration: 300,
                useInteractiveGuideline: true
            })
        ;
        chart.xAxis
            .staggerLabels(true)
            .tickFormat(function(d) {
                        return d3.time.format('%b-%y')(new Date(d))
                    });
        chart.yAxis
            // .axisLabel('Voltage (v)')

        d3.select(target_id)
          .datum(data)
          .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
}





// *************************************************************
// Functies om ajax requests af te handelen
//**************************************************************
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');




function get_and_fill() {

  //csrf token ophalen
   var csrftoken = getCookie('csrftoken');
   //wat zijn de gekozen waardes
   var val = $('#form_control').val()
   var level = $('.level').text()

  //  Verzoek sturen
    $.ajax({
      url : '/ajax_data/', // url van de ajax views
      type : "POST", // http method
      data : { csrfmiddlewaretoken : csrftoken,
        keuze: val, niveau: level
    },

    // handle a successful response
    success : function(json) {

      // show data in console
      console.log(json)
      console.log(json.data_nieuw)

      // Geraamte opzetten voor data bar graph
      data_bar =  [
        {color: "#5F9EA0",
        key:"beschikbaar",
        values: []},
        {key: 'gerealiseerd',
        color: '#FF7F50',
        values: []
        }
      ]

      // Zelfde voor line graph (= cumulatief)
      data_line =  [
        {color: "#5F9EA0",
        key:"beschikbaar",
        values: []},
        {key: 'gerealiseerd',
        color: '#FF7F50',
        values: []
        }
      ]

      $.each(json.data_nieuw, function(key, value_a){
        console.log('processing: ' + key)
        // beschikbare uren nett0 zijn: beschikbaar - ipp uren
        $.each(value_a.beschikbaar, function(i, value_b) {
              var maand = Date.parse(value_b.x)
              var beschikbaar = value_b.y
              // index uit loop gebruiken om ook timecharts op te halen
              var gerealiseerd = value_a.timecharts[i].y
              // alle verschillende soorten ipp van maand bij elkaar optellen
              var ipp = 0

              //check of er ipp's zijn, zo ja optellen bij totaal
              if (Object.keys(value_a.ipp).length > 0) {
                $.each(value_a.ipp, function(key, value_c){
                  ipp += value_c[i].y
                })
              }
              var beschikbaar_netto = beschikbaar - ipp

              // toevoegen aan data voor grafiek, als al aanwezig
              // beschikbaar en direct tegelijk
              if (data_bar[0].values.length > i) {
                data_bar[0].values[i].y += beschikbaar_netto
                data_bar[1].values[i].y += gerealiseerd

                if (i == 0) {
                  data_line[0].values[0].y = data_bar[0].values[0].y
                  data_line[1].values[0].y = data_bar[1].values[0].y
                } else {
                  data_line[0].values[i].y = data_bar[0].values[i].y + data_line[0].values[i-1].y
                  data_line[1].values[i].y = data_bar[1].values[i].y + data_line[1].values[i-1].y
                }
              } else {
              // als nog niet aanwezig
              data_bar[0].values[i] = { x: maand, y: beschikbaar_netto}
              data_bar[1].values[i] = { x: maand, y: gerealiseerd}
              data_line[0].values[i] = $.extend(true, {}, data_bar[0].values[i])
              data_line[1].values[i] = $.extend(true, {}, data_bar[1].values[i])
              }
        })
      })

    console.log('resultaten opgeteld')
    console.log(data_bar)
    console.log('resultaten opgeteld cumulatiefie')
    console.log(data_line)

     //  draw table
     draw_table(data=json, target='table')
     // draw graphs
     bar(data= data_bar, target_id='#chart')
     line(data=data_line, target_id='#chart2')


    },

    // handle a non-successful response
    error : function(xhr,errmsg,err) {
    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
    });
};


// zowel de select als de knoppen voorzien van listeners
// zodat data ververst wordt bij aanpassing
function initialise(id_select) {
   $(id_select).change(function() {
   get_and_fill();
  });
}
