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




// zowel de select als de knoppen voorzien van listeners
// zodat data ververst wordt bij aanpassing
function initialise(id_select) {
   $(id_select).change(function() {
   get_fill();
  });
}


function get_fill() {

  var target = '#medewerker_lijst'
  console.log('get fill starting')
  console.log($(target))
  console.log($(target).hasClass('dataTable'))

  if($(target).hasClass('dataTable')) {
    console.log('reloading')
    $(target).DataTable().ajax.reload()
  }
  if (! $(target).hasClass('dataTable')){
    console.log('target is not a datatable')
    $(target).DataTable({

      "ajax": {
        "url" : '/ajax_data/', // url van de ajax views
        "type" : "POST", // http method
        "data" : function () {
                var t = { "csrfmiddlewaretoken" : getCookie('csrftoken'),
                  "keuze": val = $('#form_control').val(),
                  "niveau": level = $('.level').text()}
                  console.log(t)
                  return t;
                },
        "dataSrc": function ( json ) {
          teamleden = []
          console.log('start processing json')
          $.each(json.data_nieuw, function(key, value) {
            // beschikbare uren sommeren
            var beschikbaar = value.beschikbaar.reduce(function (a, b) {return a + b.y;}, 0)

            var ipp = 0
            $.each(value.ipp, function(key, value) {
              ipp += value.reduce(function (a, b) {return a + b.y;}, 0)
            })
            // directe uren sommeren
            var direct = value.timecharts.reduce(function(a, b) {return a + b.y;}, 0)

            // Link maken van naam behandelaar
            var naam_link = "<a href=/behandelaar/" + value.pk + ">" + key + "</a>"
            // object met gegevens behandelaar aan array toevoegen
            teamlid = {
              naam:naam_link,
              beschikbaar: beschikbaar,
              ipp: ipp.toFixed(2),
              direct: direct.toFixed(2),
              productiviteit: ((direct/(beschikbaar - ipp)) *100).toFixed(2) + ' %'
            }
            teamleden.push(teamlid)
          })
          return teamleden
        }
      },
      "aoColumns": [
          { "data": "naam" }, // <-- which values to use inside object
          { "data": "beschikbaar" },
          { "data": "ipp" },
          { "data": "direct" },
          { "data": "productiviteit" }
      ],
      "language": {
          "sProcessing": "Bezig...",
          "sLengthMenu": "_MENU_ rijen weergeven",
          "sZeroRecords": "Geen resultaten",
          "sInfo": "_START_ tot _END_ van _TOTAL_ resultaten",
          "sInfoEmpty": "Geen resultaten",
          "sInfoFiltered": " (gefilterd uit _MAX_ resultaten)",
          "sInfoPostFix": "",
          "sSearch": "Zoeken:",
          "sEmptyTable": "Geen resultaten",
          "sInfoThousands": ".",
          "sLoadingRecords": "Een moment geduld aub - bezig met laden...",
          "oPaginate": {
              "sFirst": "Eerste",
              "sLast": "Laatste",
              "sNext": "Volgende",
              "sPrevious": "Vorige"
          },
          "oAria": {
              "sSortAscending":  ": oplopend sorteren",
              "sSortDescending": ": aflopend sorteren"
          }
      }

    }
    )}
}
