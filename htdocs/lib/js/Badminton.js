var DataTablesLanguage = {
  processing:     "Arbeite...",
  search:         "Filter:",
  lengthMenu:     "Zeige _MENU_ Zeilen",
  info:           "Zeile _START_ bis _END_ von _TOTAL_",
  infoEmpty:      "Keine Zeilen",
  infoFiltered:   "(aus _MAX_ Zeilen gefiltert)",
  infoPostFix:    "",
  loadingRecords: "Lade...",
  zeroRecords:    "Keine Zeilen",
  emptyTable:     "Keine Tabelle",
  paginate: {
    first:      "<<",
    previous:   "<",
    next:       ">",
    last:       ">>"
  },
};

var ValidatorOptions = {
  Vorname: {
    container: 'div[name="Vorname_Help"]',
    validators: {
      notEmpty: {message: 'Der Vorname darf nicht leer sein!'},
      stringLength: {min: 2,max: 64,message: 'Der Vorname muss zwischen %s und %s Zeichen enthalten!'},
      regexp: {regexp: /^[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF\s\-\.]+$/,message: 'Das ist kein gültiger Name!'},
    },
  },
  Nachname: {
    container: 'div[name="Nachname_Help"]',
    validators: {
      notEmpty: {message: 'Der Nachname darf nicht leer sein!'},
      stringLength: {min: 2,max: 64,message: 'Der Nachname muss zwischen %s und %s Zeichen enthalten!'},
      regexp: {regexp: /^[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF\s\-]+$/,message: 'Das ist kein gültiger Name!'},
    },
  },
  Benutzername: {
    container: 'div[name="Benutzername_Help"]',
    validators: {
      notEmpty: {message: 'Der Benutzername darf nicht leer sein!'},
      stringLength: {min: 2,max: 32,message: 'Der Benutzername muss zwischen %s und %s Zeichen enthalten!'},
      regexp: {
        regexp: /^[0-9A-Za-z@\-\_\.\+]+$/,
        message: 'Das ist kein gültiger Benutzername!',
        onSuccess: function(e, data) { data.bv.enableFieldValidators(data.field,true,'remote'); },
        onError: function(e, data) { data.bv.enableFieldValidators(data.field,false,'remote'); },
      },
      remote: {
        enabled: false,
        url: '/cgi-bin/BadmintonAjax.cgi',
        type: 'POST',
        data: function (validator) { return {Action: 'existsUsername',userid: validator.getFieldElements('UserID').val()} },
        message: 'Diesen Benutzernamen gibt es bereits!',
      }
    }
  },
  EMail: {
    container: 'div[name="EMail_Help"]',
    validators: {
      notEmpty: {message: 'Die E-Mail-Adresse darf nicht leer sein!'},
      emailAddress: {message: 'Das ist keine gültige E-Mail-Adresse!'},
      stringLength: {max: 64,message: 'Die E-Mail-Adresse darf höchstens %s Zeichen enthalten!'},
    },
  },
  Eigenbeitrag: {
    container: 'div[name="Fee_Help"]',
    validators: {
      notEmpty: {message: 'Der Eigenbeitrag darf nicht leer sein!'},
      integer: {message: 'Der Eigenbeitrag muss ganzzahlig sein!'},
      between: {
        min: 0,
        max: 200,
        message: 'Der Betrag muss zwischen 0 und 200 € sein!',
      },
    },
  },
  Setting: {
    selector: '.setting',
    validators: {
      notEmpty: {},
      integer: {},
//      between: {min: 0,max: 200},
    },
  },
  Telefon_GC: {
    container: 'div[name="Telefon_Help"]',
    validators: {
      regexp: {
        regexp: /^0[1-9][0-9]{1,3}$/i,
        message: 'Die Vorwahl muss mit 0 beginnen und 3 bis 5 Ziffern enthalten!',
      }
    }
  },
  Telefon_SC: {
    container: 'div[name="Telefon_Help"]',
    validators: {
      regexp: {
        regexp: /^[1-9][0-9]{3,7}$/i,
        message: 'Die Rufnummer darf nicht mit 0 beginnen und muss 4 bis 8 Ziffern enthalten!',
      }
    }
  },
  Geburtstag: {
    trigger: 'change',
    container: 'div[name="Geburtstag_Help"]',
    validators: {
      date: {format: 'DD.MM.YYYY',separator: '.', message: 'Das Datum muss im Format TT.MM.JJJJ sein!'},
    }
  },
  Passwort: {
    container: 'div[name="Passwort_Help"]',
    onSuccess: function(e, data) { $("input[name='Passwort2']").prop('disabled',false); },
    onError: function(e, data) { $("input[name='Passwort2']").prop('disabled',true); },
    validators: {
      notEmpty: {message: 'Das Passwort darf nicht leer sein!' },
      stringLength: {min: 8,max: 32,message: 'Das Passwort muss zwischen %s und %s Zeichen enthalten!'},
      regexp: {regexp: /^[^\s]+$/i,message: 'Das Passwort darf keine Leerzeichen enthalten!'},
    }
  },
  Passwort2: {
    container: 'div[name="Passwort2_Help"]',
    validators: {
      notEmpty: { message: 'Das Passwort darf nicht leer sein!' },
      stringLength: {min: 8,max: 32,message: 'Das Passwort muss zwischen %s und %s Zeichen enthalten!'},
      regexp: {regexp: /^[^\s]+$/i,message: 'Das Passwort darf keine Leerzeichen enthalten!'},
      identical: {field: 'Passwort',message: 'Die beiden Passwörter müssen übereinstimmen!'}
    }
  },
};


$(function() {

  $.fn.bootstrapValidator.DEFAULT_OPTIONS = $.extend({}, $.fn.bootstrapValidator.DEFAULT_OPTIONS, {
    feedbackIcons: {
      valid: 'glyphicon glyphicon-ok',
      invalid: 'glyphicon glyphicon-remove',
      validating: 'glyphicon glyphicon-refresh',
    },
    trigger: 'keyup',
  });

  $.fn.bootstrapSwitch.defaults.onColor  = 'success';
  $.fn.bootstrapSwitch.defaults.offColor = 'danger';
  $.fn.bootstrapSwitch.defaults.onText   = 'Ja';
  $.fn.bootstrapSwitch.defaults.offText  = 'Nein';
  $.fn.bootstrapSwitch.defaults.size     = 'small';

  $.cookie.json = false;

  $(document).keydown(function(event) {
    if (event.which == 13) {
      event.preventDefault();
      return false;
    }
  });

  $(document).on('click','.navbar-collapse.in',function(e) {
    if ($(e.target).is('a')) {
      $(this).collapse('hide');
    }
  });

  $("input[type='checkbox']").bootstrapSwitch();
  $("[data-toggle='tooltip']").tooltip();

  $("a[data-toggle='tab']").on('shown.bs.tab', function(e) {
    $("input[type='checkbox']").bootstrapSwitch('_width');
    $("[data-toggle='tooltip']").tooltip();
    $("input[type='checkbox']:not(:checked)").bootstrapSwitch('state',false,true);
    ttInstances = TableTools.fnGetMasters();
    for (i in ttInstances) {
      if (ttInstances[i].fnResizeRequired()) ttInstances[i].fnResizeButtons();
    }
    if (e.target.hash == '#partplayer') {
      $("input[type='checkbox'][name^='PP_Teilnahme_']").bootstrapSwitch('disabled',true);
      $("input[type='checkbox'][name^='PP_Teilnahme_']").bootstrapSwitch('indeterminate',true);
    }
    if (e.target.hash == '#playercontrib') {
//      $("input[type='checkbox']").bootstrapSwitch('disabled',true);
      $("input[type='checkbox']").bootstrapSwitch('indeterminate',true);
    }
    if (e.target.hash == '#newmatchday') $("form#NewMatchday_Date" ).trigger("reset");
    if (e.target.hash == '#persdata') $("form#PersonalData").data('bootstrapValidator').validate();
    if (e.target.hash == '#settings') $("form#Settings").data('bootstrapValidator').validate();
    if (e.target.hash == '#allactivitylog') $('#AllActivityLog').DataTable().ajax.reload();
    if (e.target.hash == '#activitylog') $('#ActivityLog').DataTable().ajax.reload();
    if (e.target.hash == '#helptext') $("#OSMap").attr('src','//www.openstreetmap.org/export/embed.html?bbox=8.20726990699768%2C50.009386951781075%2C8.225187063217163%2C50.015447288957695&layer=mapnik&marker=50.01241721590352%2C8.216228485107422');
  });

  $("div#helptext a").attr("target","_blank");


//****************************************
// Logout
//****************************************

  $("a[href='#logout']").click(function() {
    if ($.removeCookie('CGISESSID',{path: '/'})) {
      location.href = '/';
    }
  });


//****************************************
// Startseite
//****************************************

  $("button#Zusagen").click(function() {
    $.post("/cgi-bin/BadmintonAjax.cgi",{Action: 'saveParticipation',Debug: 0,Status: '1'},function (data) {
      if (data.Success) { location.href = '/'; }
//      else {}
    });
  });

  $("button#Absagen").click(function(){
    $.post("/cgi-bin/BadmintonAjax.cgi",{Action: 'saveParticipation',Debug: 0,Status: '0'}, function (data) {
      if (data.Success) { location.href = '/'; }
//      else {}
    });
  });


//****************************************
// Gast anmelden
//****************************************

  $("form#Guests")
    .on('init.form.bv',function(e,data) { data.bv.disableSubmitButtons(true); })
    .bootstrapValidator({
      submitButtons: 'button#Guest_Save',
      fields: {Vorname: ValidatorOptions['Vorname'],Nachname: ValidatorOptions['Nachname']},
    })
    .on('success.field.bv', function(e, data) { data.bv.disableSubmitButtons(!data.bv.isValid()); })
    .on('error.validator.bv',function(e, data) { data.element.data('bv.messages').find('.help-block[data-bv-for="' + data.field + '"]').hide().filter('[data-bv-validator="' + data.validator + '"]').show(); });

  $("button#Guest_Cancel").click(function() {
    $("form#Guests").data('bootstrapValidator').resetForm();
    $("form#Guests").trigger("reset");
    $("button#Guest_Save").prop("disabled",true).addClass("ui-state-disabled");
  });

  $("button#Guest_Save").click(function() {
    var formData = $("form#Guests").serialize();
//    console.log(formData);
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'saveNewGuest',
      Debug:    0,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data) }
    });
  });

  $("button[id^='DelGuest_']").click(function() {
//    console.log($(this).data('guest'));
    var date   = $(this).data('date')
    var guest  = $(this).data('guest');
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'delGuest',
      Debug:    0,
      Date:     date,
      ID:       guest,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data) }
    });
  });


//****************************************
// Weitere Teilnahme
//****************************************


  $("button#FP_Defaults").click(function() {
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'resetParticipation',
      Debug:    0,
    }, function (data) {
      if (data.Success) {
        if (data.Data == 0) {
          $("input[name^='Teilnahme_']").prop('checked',false);
          $("input[name^='Teilnahme_']").bootstrapSwitch('state',false,true);
        }
        if (data.Data == 1) {
          $("input[name^='Teilnahme_']").prop('checked',true);
          $("input[name^='Teilnahme_']").bootstrapSwitch('state',true,true);
        }
        $("button#FP_Defaults").html('Standardeinstellung wird verwendet');
        $("button#FP_Defaults").attr('disabled',true);
      }
      else { console.log(data) }
    });
  });

  $("input[name^='Teilnahme_']").on('switchChange.bootstrapSwitch',function(event,state) {
    date = this.name.substr(10);
    if (state) { status = 1; }
    else { status = 0; }
    $.post("/cgi-bin/BadmintonAjax.cgi",{
      Action:   'saveParticipation',
      Debug:    0,
      Status:   status,
      Date:     date,
    }, function (data) {
      if (data.Success) {
        $("button#FP_Defaults").html('Standardeinstellung verwenden');
        $("button#FP_Defaults").attr('disabled',false);
      }
      else {
        console.log(data);
      }
    });
  });


//****************************************
// Formular für eigene persönliche Daten
//****************************************

  $("input#PD_Geburtstag").datetimepicker({
    lazyInit: true,
    validateOnBlur: false,
    lang: 'de',
    i18n: {
      de: {
        months: ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],
        dayOfWeek: ["So.", "Mo", "Di", "Mi","Do", "Fr", "Sa."]
      }
    },
    timepicker: false,
    format: 'd.m.Y',
    closeOnDateSelect: true,
    todayButton: false,
    allowBlank: true,
    yearEnd: 2010,
  });

  $("#PD_Default_Status_Help").html('Dies ist Dein Teilnahmestatus, wenn Du keine Entscheidung triffst.');

  $("form#PersonalData")
    .on('init.form.bv',function(e,data) { data.bv.disableSubmitButtons(true); })
    .bootstrapValidator({
      submitButtons: 'button#PD_Save',
      fields: {Vorname: ValidatorOptions['Vorname'],Nachname: ValidatorOptions['Nachname'],EMail: ValidatorOptions['EMail'],Benutzername: ValidatorOptions['Benutzername'],Telefon_GC: ValidatorOptions['Telefon_GC'],Telefon_SC: ValidatorOptions['Telefon_SC'],Geburtstag: ValidatorOptions['Geburtstag']},
    })
    .on('success.field.bv', function(e, data) { data.bv.disableSubmitButtons(!data.bv.isValid()); })
    .on('error.validator.bv',function(e, data) { data.element.data('bv.messages').find('.help-block[data-bv-for="' + data.field + '"]').hide().filter('[data-bv-validator="' + data.validator + '"]').show(); });

  $( "button#PD_Cancel" ).click(function() {
    $("form#PersonalData").data('bootstrapValidator').resetForm();
    $("form#PersonalData").trigger("reset");
    $("form#PersonalData").data('bootstrapValidator').validate();
  });

  $( "button#PD_Save" ).click(function() {
    var formData = $("form#PersonalData").serialize();
//    console.log(formData);
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'savePersonalData',
      Debug:    0,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
//      else {}
    });
  });


//****************************************
// Formular für Passwortänderung
//****************************************

  $("input#PW_Passwort").keyup(function() {
    $("input#PW_Passwort2").val('');
    $("form#ChangePassword").data('bootstrapValidator').resetField('Passwort2',true);
  });

  $("form#ChangePassword")
    .on('init.form.bv', function(e, data) { data.bv.disableSubmitButtons(true); })
    .bootstrapValidator({
      submitButtons: 'button#PW_Save',
      fields: {Passwort: ValidatorOptions['Passwort'],Passwort2: ValidatorOptions['Passwort2']},
    })
    .on('success.field.bv', function(e, data) { data.bv.disableSubmitButtons(!data.bv.isValid()); })
    .on('error.validator.bv', function(e, data) { data.element.data('bv.messages').find('.help-block[data-bv-for="' + data.field + '"]').hide().filter('[data-bv-validator="' + data.validator + '"]').show(); });


  $( "button#PW_Cancel" ).click(function() {
    $("form#ChangePassword").data('bootstrapValidator').resetForm();
    $("form#ChangePassword").trigger("reset");
    $("button#PW_Save").prop("disabled",true).addClass("ui-state-disabled");
    $("input#PW_Passwort2").prop('disabled',true);
  });

  $( "button#PW_Save" ).click(function() {
    var formData = $("form#ChangePassword").serialize();
//    console.log(formData);
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'savePassword',
      Debug:    0,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
//      else {}
    });
  });


//****************************************
// Teilnehmerübersicht
//****************************************

  $('#ListPlayers').DataTable({
    paging: false,
    info: false,
//    search: { smart: false},
    order: [1,'asc'],
    columns: [
      { className: 'text-right',data: {},orderable: false },
//      { className: "text-right",data: {_: 'ID'} },
      { className: "text-left text-nowrap",data: {_: 'Name.display',sort: 'Name.sort',type: 'Name.sort'} },
      { className: 'text-center',data: {_: 'Aktiv'} },
      { className: "text-left",data: {_: 'Benutzername'},orderable: false },
      { className: "text-left",data: {_: 'EMail'},render: function (data,type,full,meta) { return '<a href="mailto:'+data+'">'+data+'</a>';},orderable: false },
      { className: "text-right text-nowrap",data: {_: 'Telefon'},render: function (data,type,full,meta) { return '<a href="tel://'+data.link+'">'+data.display+'</a>';},orderable: false },
//      { className: "text-left text-nowrap",data: {_: 'Eintritt'} },
//      { className: "text-center",data: {_: 'DefaultStatus'} },
    ],
    fnRowCallback: function(nRow,aData,iDisplayIndex,iDisplayIndexFull) {
      var index = iDisplayIndex + 1;
      $('td:eq(0)',nRow).html(index);
      return nRow;
    },
    language: DataTablesLanguage,
    ajax: {
      url: "/cgi-bin/BadmintonAjax.cgi",
      type: 'POST',
      data: {
        Action:   'getPlayerList',
        Debug:    0,
      },
      dataSrc: 'Data',
    },
    dom: 'T<"clear">lfrtip',
    tableTools: {
      sSwfPath: '/lib/jquery-plugins/datatables-extensions/TableTools/swf/copy_csv_xls_pdf.swf',
      oSelectorOpts: { filter: 'applied' },
      aButtons: [
        { sExtends: 'copy',mColumns: [1,2,3,4,5],oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'csv',mColumns: [1,2,3,4,5],oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'xls',mColumns: [1,2,3,4,5],oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'pdf',mColumns: [1,2,3,4,5],oSelectorOpts: { filter: 'applied' },sPdfOrientation: 'landscape',sPdfMessage: "Teilnehmerübersicht (Stand: " + (new Date()).toLocaleString() + ")",sFileName: "Badminton-Teilnehmerübersicht.pdf" },
        { sExtends: 'print',mColumns: [1,2,3,4,5],oSelectorOpts: { filter: 'applied' } },
      ],
    },
  });


//****************************************
// Activity Log
//****************************************

  $('#ActivityLog').DataTable({
    deferRender: true,
    ordering: false,
    lengthMenu: [ [10, 20, 50, 100, -1], [10, 20, 50, 100, "Alle"] ],
    pageLength: 10,
    pagingType: 'full',
    columns: [
      { className: 'dt-left text-nowrap',data: 'Timestamp' },
      { className: 'dt-left text-nowrap',data: 'ByUser' },
      { className: 'dt-left text-nowrap',data: 'Activity' },
    ],
    language: DataTablesLanguage,
    ajax: {
      url: "/cgi-bin/BadmintonAjax.cgi",
      type: 'POST',
      data: {
        Action:   'getActivityLog',
        Debug:    0,
      },
      dataSrc: 'Data',
    }
  });

});
