$(function() {

//****************************************
// Einstellungen
//****************************************

  $("form#Settings")
    .on('init.form.bv', function(e, data) { data.bv.disableSubmitButtons(true); })
    .bootstrapValidator({
      submitButtons: 'button#ST_Save',
      fields: {Setting: ValidatorOptions['Setting']},
    })
    .on('success.field.bv', function(e, data) { data.bv.disableSubmitButtons(!data.bv.isValid()); })
    .on('error.validator.bv', function(e, data) { data.element.data('bv.messages').find('.help-block[data-bv-for="' + data.field + '"]').hide().filter('[data-bv-validator="' + data.validator + '"]').show(); });

  $( "button#ST_Cancel" ).click(function() {
    $("form#Settings").data('bootstrapValidator').resetForm();
    $("form#Settings").trigger("reset");
    $("form#Settings").data('bootstrapValidator').validate();
  });

  $( "button#ST_Save" ).click(function() {
    var formData = $("form#Settings").serialize();
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'saveSettings',
      Debug:    0,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });




//****************************************
// Spielzeiten festlegen
//****************************************

  var SetCourtsDefault = $("input[type='radio'][name='CourtsSet']:checked").val();
  getCourtsExplanation(SetCourtsDefault);

  $("input[type='radio'][name='CourtsSet']").change(function() {
    changeCourtsSelection($(this).parent());
    getCourtsExplanation($(this).val());
  });

  $("select[name='CourtsSetScroll']").change(function() {
    $("input[type='radio'][name='CourtsSet']").val($(this).val());
    getCourtsExplanation($(this).val());
  });

  $("button[name='SC_Save']").click(function() {
    var date   = $(this).data('date');
    var formData = $("form#SetCourts_" + date ).serialize();
//    console.log(formData);
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'saveCourts',
      Debug:    0,
      Date: date,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });

  $("button[name='SC_Cancel']").click(function() {
    var date = $(this).data('date');
    $("form#SetCourts_" + date ).trigger("reset");
    changeCourtsSelection($("input[type='radio'][name='CourtsSet'][value=" + SetCourtsDefault + "]").parent());
  });


//****************************************
// Spieltag abschließen
//****************************************

  var CourtsDefault = $("input[type='radio'][name='Courts']:checked").val();

  $("input[type='radio'][name='Courts']").change(function() {
    changeCourtsSelection($(this).parent());
  });

  $("select[name='CourtsScroll']").change(function() {
    $("input[type='radio'][name='Courts']").val($(this).val());
  });

  $("button[name='CM_Save']").click(function() {
    var date   = $(this).data('date');
    var formData = $("form#CloseMatchday_" + date ).serialize();
    $("input[name^='Player_']").each(function() {
      if ($(this).data('date') == date) {
        if (!this.checked) formData += '&' + this.name + '=off';
      }
    });
    $("input[name^='Guest_']").each(function() {
      if ($(this).data('date') == date) {
        if (!this.checked) formData += '&' + this.name + '=off';
      }
    });
//    console.log(date,formData);
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'saveMatchday',
      Debug:    0,
      Date: date,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });

  $("button[name='CM_Cancel']").click(function() {
    var date = $(this).data('date');
    $("form#CloseMatchday_" + date ).trigger("reset");
    changeCourtsSelection($("input[type='radio'][name='Courts'][value=" + CourtsDefault + "]").parent());
  });


//****************************************
// Formular für zukünftige Spieltage
//****************************************

  $("input[name^='Matchday_']").on("switchChange.bootstrapSwitch",function(event,state) {
    date = this.name.substr(9);
    if (state) { status = 1; }
    else { status = 0; }
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'saveFutureMatchday',
      Debug:    0,
      Date:     date,
      Status:   status,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });


//****************************************
// Formular für neue Spieltage
//****************************************

  $("select#NewMatchday_Date").change(function() {
    if ($(this).val() == "") {
      $("button#NewMatchday_Save" ).prop('disabled',true).addClass("ui-state-disabled");
      $("button#NewMatchday_Cancel" ).prop('disabled',true).addClass("ui-state-disabled");
    }
    else {
      $("button#NewMatchday_Save" ).prop('disabled',false).removeClass("ui-state-disabled");
      $("button#NewMatchday_Cancel" ).prop('disabled',false).removeClass("ui-state-disabled");
    }
  });

  $( "button#NewMatchday_Cancel" ).click(function() {
    $("select#NewMatchday_Date").val("");
    $("select#NewMatchday_Date").change();
  });

  $( "button#NewMatchday_Save" ).click(function() {
    var formData = $("form#NewMatchday").serialize();
    $.post("/cgi-bin/BadmintonAjax.cgi",{
      Action:   'saveNewMatchday',
      Debug:    0,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });


//****************************************
// Öffnen abgeschlossener Spieltage
//****************************************

  $("button[id^='PM_ReopenMatchday_']").click(function() {
    date = this.id.substr(18);
//    console.log(date);
    $("div#Panel_PM_" + date).hide('slow');
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'reopenMatchday',
      Debug:    0,
      Date: date,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });


//****************************************
// Formular für neuen Teilnehmer
//****************************************

  $("form#NewPlayer")
    .on('init.form.bv', function(e, data) { data.bv.disableSubmitButtons(true); })
    .bootstrapValidator({
      submitButtons: 'button#NP_Save',
      fields: {Vorname: ValidatorOptions['Vorname'],Nachname: ValidatorOptions['Nachname'],EMail: ValidatorOptions['EMail'],Benutzername: ValidatorOptions['Benutzername']},
    })
    .on('success.field.bv', function(e, data) { data.bv.disableSubmitButtons(!data.bv.isValid()); })
    .on('error.validator.bv', function(e, data) { data.element.data('bv.messages').find('.help-block[data-bv-for="' + data.field + '"]').hide().filter('[data-bv-validator="' + data.validator + '"]').show(); });

  $( "button#NP_Cancel" ).click(function() {
    $("form#NewPlayer").data('bootstrapValidator').resetForm();
    $("form#NewPlayer").trigger("reset");
    $("button#NP_Save").prop("disabled",true).addClass("ui-state-disabled");
  });

  $( "button#NP_Save" ).click(function() {
    var formData = $("form#NewPlayer").serialize();
    $.post( "/cgi-bin/BadmintonAjax.cgi", {
      Action:   'saveNewPlayer',
      Debug:    0,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });


//****************************************
// Teilnehmerdaten bearbeiten
//****************************************

  $("form#EditPlayer")
    .on('init.form.bv', function(e, data) { data.bv.disableSubmitButtons(true); })
    .bootstrapValidator({
      submitButtons: 'button#EP_Save',
      fields: {Vorname: ValidatorOptions['Vorname'],Nachname: ValidatorOptions['Nachname'],EMail: ValidatorOptions['EMail'],Benutzername: ValidatorOptions['Benutzername'],Fee: ValidatorOptions['Eigenbeitrag']},
    })
    .on('success.field.bv', function(e, data) { data.bv.disableSubmitButtons(!data.bv.isValid()); })
    .on('error.validator.bv', function(e, data) { data.element.data('bv.messages').find('.help-block[data-bv-for="' + data.field + '"]').hide().filter('[data-bv-validator="' + data.validator + '"]').show(); });

  $("select#SP_UserID").change(function() {
    $("form#EditPlayer").data('bootstrapValidator').resetForm();
    $("button#EP_Save" ).prop('disabled',true).addClass("ui-state-disabled");
    $("button#EP_Cancel" ).prop('disabled',true).addClass("ui-state-disabled");
    if ($(this).val() == "") {
      $("form#EditPlayer").trigger("reset");
      $("input#EP_Vorname").prop('disabled',true);
      $("input#EP_Nachname").prop('disabled',true);
      $("input#EP_EMail").prop('disabled',true);
      $("input#EP_Benutzername").prop('disabled',true);
      $("input#EP_Fee").prop('disabled',true);
      $("input#EP_Aktiv").prop('disabled',true);
      $("input#EP_Aktiv").bootstrapSwitch('disabled',true);
      $("input#EP_Default_Status").bootstrapSwitch('state',false,true);
      $("input#EP_Default_Status").prop('checked',false);
      $("input#EP_Default_Status").bootstrapSwitch('disabled',true);
      $("input#EP_Default_Status").prop('disabled',true);
      $("input#EP_Passwort").bootstrapSwitch('state',false,true);
      $("input#EP_Passwort").prop('checked',false);
      $("input#EP_Passwort").bootstrapSwitch('disabled',true);
      $("input#EP_Passwort").prop('disabled',true);
    }
    else {
      $("input#EP_UserID").val($("select#SP_UserID").val());
      $("input#EP_Vorname").prop('disabled',false);
      $("input#EP_Nachname").prop('disabled',false);
      $("input#EP_EMail").prop('disabled',false);
      $("input#EP_Benutzername").prop('disabled',false);
      $("input#EP_Fee").prop('disabled',false);
      $("input#EP_Aktiv").prop('disabled',false);
      $("input#EP_Aktiv").bootstrapSwitch('disabled',false);
      $("input#EP_Default_Status").prop('disabled',false);
      $("input#EP_Default_Status").bootstrapSwitch('disabled',false);
      $("input#EP_Passwort").prop('disabled',false);
      $("input#EP_Passwort").bootstrapSwitch('disabled',false);
      $("input#EP_Passwort").bootstrapSwitch('state',false,true);
      $("button#EP_Cancel" ).prop('disabled',false).removeClass("ui-state-disabled");
      $.post("/cgi-bin/BadmintonAjax.cgi",{
        Action:   'getPlayerData',
        Debug:    0,
        UserID:   $("input#EP_UserID").val(),
      }, function (data) {
        if (data.Success) {
//          console.log(data.Result);
          $("input#EP_Vorname").val(data.Result['Firstname']);
          $("input#EP_Nachname").val(data.Result['Lastname']);
          $("input#EP_EMail").val(data.Result['EMail']);
          $("input#EP_Benutzername").val(data.Result['username']);
          $("input#EP_Fee").val(data.Result['Fee']);
          if (data.Result['Default_Status'] == "1") {
            $("input#EP_Default_Status").prop('checked',true);
            $("input#EP_Default_Status").bootstrapSwitch('state',true,true);
          }
          if (data.Result['Default_Status'] == "0") {
            $("input#EP_Default_Status").bootstrapSwitch('state',false,true);
            $("input#EP_Default_Status").prop('checked',false);
          }
          if (data.Result['Active'] == "1") {
            $("input#EP_Aktiv").prop('checked',true);
            $("input#EP_Aktiv").bootstrapSwitch('state',true);
            onActivate(true);
          }
          if (data.Result['Active'] == "0") {
            $("input#EP_Aktiv").bootstrapSwitch('state',false);
            $("input#EP_Aktiv").prop('checked',false);
            onActivate(false);
          }
          $("form#EditPlayer").data('bootstrapValidator').validate();
        }
        else { console.log(data); }
      });
    }
  });

  $("input#EP_Aktiv").on('switchChange.bootstrapSwitch',function(event,state) {
     onActivate(state);
  });

  $( "button#EP_Cancel" ).click(function() {
    $("select#SP_UserID").val("");
    $("select#SP_UserID").change();
  });

  $( "button#EP_Save" ).click(function() {
    var formData = $("form#EditPlayer").serialize();
    $.post("/cgi-bin/BadmintonAjax.cgi",{
      Action:   'saveEditPlayer',
      Debug:    0,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });


//****************************************
// Teilnehmerbeiträge pflegen
//****************************************

  $("select#PC_UserID").change(function() {
    $("input[name*=Status_]").bootstrapSwitch('indeterminate',true);
    $("button#PC_Save" ).prop('disabled',true).addClass("ui-state-disabled");
    $("button#PC_Cancel" ).prop('disabled',true).addClass("ui-state-disabled");
    if ($(this).val() == "") {
      $("span[id^=Fee]").html('');
      $("span[id^=Late]").html('');
      $("span[id^=Guests]").html('');
      $("form#PlayerContrib").trigger("reset");
      $("input[name*=Status_]").prop('disabled',true).bootstrapSwitch('disabled',true);
    }
    else {
      $("input#PC_UserID").val($("select#PC_UserID").val());
      var formData = $("form#PlayerContrib").serialize();
//      console.log(formData);
      $("button#PC_Save" ).prop('disabled',false).removeClass("ui-state-disabled");
      $("button#PC_Cancel" ).prop('disabled',false).removeClass("ui-state-disabled");
      $.post("/cgi-bin/BadmintonAjax.cgi",{
        Action:   'getContributions',
        Debug:    0,
        FormData: formData,
      }, function (data) {
        if (data.Success) {
//          console.log(data.Data);
          for (year in data.Data) {
//            console.log(data.Data[year]);
            $("span#Fee_" + year).html(data.Data[year].Fee);
            $("span#Late_" + year).html(data.Data[year].Late);
            $("span#Guests_" + year).html(data.Data[year].Guests);
            if (data.Data[year].Fee > 0) {
              $("input#PC_FeeStatus_" + year).prop('disabled',false).bootstrapSwitch('disabled',false);
              $("input#PC_FeeStatus_" + year).bootstrapSwitch('indeterminate',false);
              if (data.Data[year].FeeStatus == "1") {
                $("input#PC_FeeStatus_" + year).prop('checked',true);
                $("input#PC_FeeStatus_" + year).bootstrapSwitch('state',true,true);
              }
              if (data.Data[year].FeeStatus == "0") {
                $("input#PC_FeeStatus_" + year).bootstrapSwitch('state',false,true);
                $("input#PC_FeeStatus_" + year).prop('checked',false);
              }
            }
            if (data.Data[year].Late > 0) {
              $("input#PC_LateStatus_" + year).prop('disabled',false).bootstrapSwitch('disabled',false);
              $("input#PC_LateStatus_" + year).bootstrapSwitch('indeterminate',false);
              if (data.Data[year].LateStatus == "1") {
                $("input#PC_LateStatus_" + year).prop('checked',true);
                $("input#PC_LateStatus_" + year).bootstrapSwitch('state',true,true);
              }
              if (data.Data[year].LateStatus == "0") {
                $("input#PC_LateStatus_" + year).bootstrapSwitch('state',false,true);
                $("input#PC_LateStatus_" + year).prop('checked',false);
              }
            }
            if (data.Data[year].Guests > 0) {
              $("input#PC_GuestsStatus_" + year).prop('disabled',false).bootstrapSwitch('disabled',false);
              $("input#PC_GuestsStatus_" + year).bootstrapSwitch('indeterminate',false);
              if (data.Data[year].GuestsStatus == "1") {
                $("input#PC_GuestsStatus_" + year).prop('checked',true);
                $("input#PC_GuestsStatus_" + year).bootstrapSwitch('state',true,true);
              }
              if (data.Data[year].GuestsStatus == "0") {
                $("input#PC_GuestsStatus_" + year).bootstrapSwitch('state',false,true);
                $("input#PC_GuestsStatus_" + year).prop('checked',false);
              }
            }
          }
        }
        else { console.log(data); }
      });
    }
  });

  $( "button#PC_Cancel" ).click(function() {
    $("select#PC_UserID").val("");
    $("select#PC_UserID").change();
  });

  $( "button#PC_Save" ).click(function() {
    var formData = $("form#PlayerContrib").serialize();
    $("input[name*='Status_']").each(function() {
      if (!this.checked) formData += '&' + this.name + '=off';
    });
    $.post("/cgi-bin/BadmintonAjax.cgi",{
      Action:   'saveContributions',
      Debug:    0,
      FormData: formData,
    }, function (data) {
      if (data.Success) { location.href = '/'; }
      else { console.log(data); }
    });
  });


//****************************************
// Für Teilnehmer abstimmen
//****************************************

  $("select#SP2_UserID").change(function() {
    if ($(this).val() == "") {
      $("#PP_Default").html('');
      $("input[type='checkbox'][name^='PP_Teilnahme_']").bootstrapSwitch('disabled',true);
      $("form#PartPlayer").trigger("reset");
    }
    else {
      $("input[type='checkbox'][name^='PP_Teilnahme_']").bootstrapSwitch('disabled',false);
      $.post("/cgi-bin/BadmintonAjax.cgi",{
        Action:   'getPlayerParticipation',
        Debug:    0,
        UserID:   $("select#SP2_UserID").val(),
      }, function (data) {
        if (data.Success) {
//          console.log(data.Data);
          $("#PP_Default").html('Standard-Teilnahmestatus: ' + data.Message);
          for (date in data.Data) {
            Name = "PP_Teilnahme_" + date;
//            console.log(date);
//            console.log(data.Data[date]);
            if (data.Data[date] == '-1') $("input[name=" + Name + "]").bootstrapSwitch('indeterminate',true);
            if (data.Data[date] == '0') {
              $("input[name=" + Name + "]").bootstrapSwitch('indeterminate',false);
              $("input[name=" + Name + "]").bootstrapSwitch('state',false,true);
            }
            if (data.Data[date] == '1') {
              $("input[name=" + Name + "]").bootstrapSwitch('indeterminate',false);
              $("input[name=" + Name + "]").bootstrapSwitch('state',true,true);
            }
          }
        }
        else {
          console.log(data);
        }
      });
    }
  });

  $("input[type='checkbox'][name^='PP_Teilnahme_']").on('switchChange.bootstrapSwitch',function(event,state) {
    date = this.name.substr(13);
    if (state) { status = 1; }
    else { status = 0; }
    $.post("/cgi-bin/BadmintonAjax.cgi",{
      Action:   'saveParticipation',
      Debug:    0,
      UserID:   $("select#SP2_UserID").val(),
      Status:   status,
      Date:     date,
    }, function (data) {
      if (data.Success) {
      }
      else {
        console.log(data);
      }
    });
  });

//****************************************
// Teilnahmebericht
//****************************************

  $('#ListParticipation').DataTable({
    deferRender: true,
//    order: [[0,'desc'],[1,'asc']],
    ordering: false,
    lengthMenu: [ [10, 20, 50, 100, -1], [10, 20, 50, 100, "Alle"] ],
    pageLength: 10,
    pagingType: 'full',
    columns: [
      { className: 'dt-left text-nowrap',data: 'Timestamp' },
      { className: 'text-left text-nowrap',data: 'ForUser' },
//      { className: 'text-center',data: {_: 'Aktiv'} },
      { className: 'text-center',data: 'Status' },
      { className: 'text-center',data: 'OnTime' },
    ],
    language: DataTablesLanguage,
    ajax: {
      url: "/cgi-bin/BadmintonAjax.cgi",
      type: 'POST',
      data: {
        Action:   'getParticipationList',
        Debug:    0,
      },
      dataSrc: 'Data',
    },
    dom: 'lfrt<"clear">iTp',
    tableTools: {
      sSwfPath: '/common-lib/jquery-plugins/datatables-extensions/TableTools/swf/copy_csv_xls_pdf.swf',
      oSelectorOpts: { filter: 'applied' },
      aButtons: [
        { sExtends: 'copy',oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'csv',oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'xls',oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'pdf',oSelectorOpts: { filter: 'applied' },sPdfOrientation: 'portrait',sPdfMessage: "Teilnahmebericht (Stand: " + (new Date()).toLocaleString() + ")",sFileName: "Badminton-Teilnahmebericht.pdf" },
        { sExtends: 'print',oSelectorOpts: { filter: 'applied' } },
      ],
    },
  });


//****************************************
// Activity Log
//****************************************

  $('#AllActivityLog').DataTable({
    deferRender: true,
    ordering: false,
    lengthMenu: [ [10, 50, 100, 500, -1], [10, 50, 100, 500, "Alle"] ],
    pageLength: 10,
    pagingType: 'full_numbers',
    columns: [
//      { className: 'dt-left text-nowrap',data: 'Timestamp',render: function (data,type,row,meta) { if ( type === 'display' || type === 'filter' ) return formatDate('Medium',new Date( data * 1000 )); return data; } },
      { className: 'dt-left text-nowrap',data: 'Timestamp' },
      { className: 'dt-left text-nowrap',data: 'ByUser' },
      { className: 'dt-left text-nowrap',data: 'ForUser' },
      { className: 'dt-left text-nowrap',data: 'Activity' },
    ],
    language: DataTablesLanguage,
    ajax: {
      url: "/cgi-bin/BadmintonAjax.cgi",
      type: 'POST',
      data: {
        Action:   'getAllActivityLog',
        Debug:    0,
      },
      dataSrc: 'Data',
    },
    dom: 'lfrt<"clear">iTp',
    tableTools: {
      sSwfPath: '/common-lib/jquery-plugins/datatables-extensions/TableTools/swf/copy_csv_xls_pdf.swf',
      oSelectorOpts: { filter: 'applied' },
      aButtons: [
        { sExtends: 'copy',oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'csv',oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'xls',oSelectorOpts: { filter: 'applied' } },
        { sExtends: 'pdf',oSelectorOpts: { filter: 'applied' },sPdfOrientation: 'landscape',sPdfMessage: "Protokoll (Stand: " + (new Date()).toLocaleString() + ")",sFileName: "Badminton-Protokoll.pdf" },
        { sExtends: 'print',oSelectorOpts: { filter: 'applied' } },
      ],
    },
  });

});

//****************************************
// Hilfsfunktionen
//****************************************

function formatDate(format,date) {
  if (format == 'Medium') {
    return date.toLocaleString('de-DE',{weekday: 'short'}) + ', ' +
           date.toLocaleString('de-DE',{day: 'numeric'}) + '. ' +
           date.toLocaleString('de-DE',{month: 'short'}) + '. ' +
           date.toLocaleString('de-DE',{year: 'numeric'}) + ', ' +
           date.toLocaleTimeString('de-DE');
//           date.toLocaleString('de-DE',{hour: '2-digit',minute: '2-digit',second: '2-digit'});
  }
}

function changeCourtsSelection(ele) {
  $(ele).siblings().removeClass('btn-primary active');
  $(ele).siblings().addClass('btn-default');
  $(ele).removeClass('btn-default');
  $(ele).addClass('btn-primary active');
}

function togglePasswordVisibility(id) {
  var passwordField = document.getElementById(id);
  var value = passwordField.value;
  if(passwordField.type == 'password') {
    passwordField.type = 'text';
  }
  else {
    passwordField.type = 'password';
  }
  passwordField.value = value;
}

function onActivate(state) {
  if (state === true) {
    $("input#EP_Default_Status").prop('disabled',false);
    $("input#EP_Default_Status").bootstrapSwitch('disabled',false);
    $("input#EP_Passwort").prop('disabled',false);
    $("input#EP_Passwort").bootstrapSwitch('disabled',false);
    $("input#EP_Passwort").bootstrapSwitch('state',false,true);
  }
  else {
    $("input#EP_Default_Status").bootstrapSwitch('state',false,true);
    $("input#EP_Default_Status").prop('checked',false);
    $("input#EP_Default_Status").bootstrapSwitch('disabled',true);
    $("input#EP_Default_Status").prop('disabled',true);
    $("input#EP_Passwort").bootstrapSwitch('state',false,true);
    $("input#EP_Passwort").prop('checked',false);
    $("input#EP_Passwort").bootstrapSwitch('disabled',true);
    $("input#EP_Passwort").prop('disabled',true);
  }
}

function getCourtsExplanation(courts) {
  var prefix = courts + ' Spielzeit';
  if (courts > 1) prefix += 'en';
  prefix += ' = ';
  var explanation;
  if (courts == '1') explanation = '1 Platz, 1 Spielzeit';
  if (courts == '2') explanation = '1 Platz, 2 Spielzeiten';
  if (courts == '3') explanation = '1 Platz, 3 Spielzeiten';
  if (courts == '4') explanation = '1 Platz, 3 Spielzeiten + 1 Platz, 1 Spielzeit';
  if (courts == '5') explanation = '1 Platz, 3 Spielzeiten + 1 Platz, 2 Spielzeiten';
  if (courts == '6') explanation = '2 Plätze, 3 Spielzeiten';
  if (courts == '7') explanation = '2 Plätze, 3 Spielzeiten + 1 Platz, 1 Spielzeit';
  if (courts == '8') explanation = '2 Plätze, 3 Spielzeiten + 1 Platz, 2 Spielzeiten';
  if (courts == '9') explanation = '3 Plätze, 3 Spielzeiten';
  if (courts == '10') explanation = '3 Plätze, 3 Spielzeiten + 1 Platz, 1 Spielzeit';
  if (courts == '11') explanation = '3 Plätze, 3 Spielzeiten + 1 Platz, 2 Spielzeiten';
  if (courts == '12') explanation = '4 Plätze, 3 Spielzeiten';
  if (courts == '13') explanation = '4 Plätze, 3 Spielzeiten + 1 Platz, 1 Spielzeit';
  if (courts == '14') explanation = '4 Plätze, 3 Spielzeiten + 1 Platz, 2 Spielzeiten';
  if (courts == '15') explanation = '5 Plätze, 3 Spielzeiten';
  $("#SetCourtsExplanation").html(explanation);
  $("#SetCourtsExplanationXS").html(explanation);

}
