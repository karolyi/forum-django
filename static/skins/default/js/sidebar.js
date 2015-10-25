/*global define */
'use strict';
define(['common'], function (common) {
  var $ = common.$;

  var Instance = function (options) {
    var self = this;

    this.onClickButtonToggle = function () {
      self.toggleSidebar();
    };

    this.onClickSidebarOverlay = function () {
      self.toggleSidebar();
    };

    this.toggleSidebar = function () {
      self.jqSidebar.toggleClass('in');
      self.jqSidebarOverlay.toggleClass('in');
    };

    this.initialize = function (options) {
      this.options = options;
      this.jqButtonToggle = $(options.selectors.buttonToggle)
        .click(this.onClickButtonToggle);
      this.jqSidebar = $(options.selectors.sidebarWrapper);
      this.jqSidebarOverlay = $(options.selectors.sidebarOverlay)
        .click(this.onClickSidebarOverlay);
    };

    this.initialize(options);
  };

  var init = function (options) {
    // Wait for the DOMReady, then run the callback with the options
    $.when($.ready.promise()).then(function () {
      new Instance(options);
    });
  };

  return {
    init: init
  };
});
