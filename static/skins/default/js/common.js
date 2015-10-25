/*global require, define, gettext, Intl */
'use strict';
require.config({
  paths: {
    jquery: '../../../bower_components/jquery/dist/jquery',
    bootstrap: '../../../bower_components/bootstrap-sass/assets/javascripts/bootstrap',
    'strip-json-comments': '../../../bower_components/strip-json-comments/strip-json-comments',
    'moment': '../../../bower_components/moment/moment',
  },
  shim: {
    bootstrap: {
      deps: ['jquery'],
    },
    'strip-json-comments': {
      exports: 'stripJsonComments'
    },
  }
});
define([
  'jquery', 'strip-json-comments', 'moment', 'bootstrap'], function (
  $, stripJsonComments, moment) {
  var options = {};

  var onReadyPage = function () {};

  var init = function (initOptions) {
    // Don't overwrite the original options reference, just update the keys
    for (var key in initOptions) {
      if (initOptions.hasOwnProperty(key)) {
        options[key] = initOptions[key];
      }
    }
    if (window.Intl) {
      var intlNumberformat = new Intl.NumberFormat(options.languageInfo.code);
      numberFormat = function (input) {
        return intlNumberformat.format(input);
      };
    }
  };

  // No Intl for Safari: http://caniuse.com/#search=intl
  var numberFormat = function (input) {
    return input;
  };

  /**
   * Return the locale number formatted number or a translated '(no data)'
   * @param  {Number} input The input number.
   * @return {String}       The formatted string or '(no data)' translated.
   */
  var numberOrNoData = function (input) {
    if (input === null) {
      return gettext('(no data)');
    }
    return numberFormat(input);
  };

  /**
   * Update a hidden CSRF token in a form, using the cookie value
   * @return {string} The CSRF cookie value
   */
  var updateCsrfToken = function (jqElement) {
    var csrfToken = getCookie('csrftoken');
    if (jqElement) {
      jqElement.val(csrfToken);
    }
    return csrfToken;
  };

  /**
   * Cookie getter function from here:
   * https://docs.djangoproject.com/en/dev/ref/csrf/
   * @param  {string} name The cookie name
   * @return {string}      Cookie value
   */
  var getCookie = function (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = $.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  var setCookie = function (name, value, expirationDays) {
    var now = new Date();
    now.setTime(now.getTime() + (expirationDays * 24 * 60 * 60 * 1000));
    var expires = 'expires=' + now.toUTCString();
    document.cookie = name + '=' + value + '; ' + expires;
  };

  $.when($.ready.promise()).then(onReadyPage);
  return {
    $: $,
    stripJsonComments: stripJsonComments,
    moment: moment,
    init: init,
    options: options,
    numberFormat: numberFormat,
    numberOrNoData: numberOrNoData,
    updateCsrfToken: updateCsrfToken,
    getCookie: getCookie,
    setCookie: setCookie
  };
});
