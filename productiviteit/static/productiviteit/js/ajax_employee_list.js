// Functie om cookie uit de sessiedata te halen
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
      // console.log(json)
      console.log(json.data_nieuw)

      // Data is per behandelaar, met daaronder nog verschillende categorieen
      // Hier samenvatten per behandelaar
      teamleden = []
      console.log('start processing json')
      $.each(json.data_nieuw, function(key, value) {
        // beschikbare uren sommeren
        var beschikbaar = value.beschikbaar.reduce(function (a, b) {return a + b.y;}, 0)
        // console.log('beschikbare uren: ' + beschikbaar)
        // ipp uren sommeren
        var ipp = 0
        $.each(value.ipp, function(key, value) {
          ipp += value.reduce(function (a, b) {return a + b.y;}, 0)
        })
        // directe uren sommeren
        var direct = value.timecharts.reduce(function(a, b) {return a + b.y;}, 0)

        // object met gegevens behandelaar aan array toevoegen
        teamlid = {
          naam:key,
          beschikbaar: beschikbaar,
          ipp: ipp,
          direct: direct,
          productiviteit: (direct/(beschikbaar - ipp))
        }
        console.log(teamlid)
        teamleden.push(teamlid)
      })

    },

    // handle a non-successful response
    error : function(xhr,errmsg,err) {
    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
  });
};

console.log('ajax_employee_list.js loaded...')
