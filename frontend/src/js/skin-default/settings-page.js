/* global Forum */
import $ from 'jquery'
import { init as richTextAreaInit } from './rich-text-area'
import 'bootstrap/js/src/tooltip'
import 'bootstrap/js/src/alert'
// const paginator = require('./paginator')
// const userName = require('./userName')
// const timeActualizer = require('./time-actualizer')
// const popOverHoverContent = require('./popover-hovercontent')

export class Instance {
  constructor(options) {
    this.options = options
  }

  searchUsernames(params, success, failure) {
    const ajaxData = {
      name_contains: params.data.term,
      page: params.data.page || 1,
    }
    $.when($.ajax({
      url: this.options.urls.userSearch,
      data: ajaxData,
      dataType: 'json',
    })).then(success, failure)
  }

  initSelectMenus() {
    $('#id_ignored_users').select2({
      // debug: true,
      ajax: {
        delay: 250,
        transport: :: this.searchUsernames,
      },
      closeOnSelect: false,
      minimumInputLength: 2,
      placeholder: Forum.django.gettext('Choose usernames to ignore...'),
    })
    $('#id_friended_users').select2({
      ajax: {
        delay: 250,
        transport: :: this.searchUsernames,
      },
      closeOnSelect: false,
      minimumInputLength: 2,
      placeholder: Forum.django.gettext('Choose usernames to befriend...'),
    })
  }

  initTextAreas() {
    this.introMdTextArea = $('#id_introduction_md_all')
    richTextAreaInit({
      jqWrapper: this.introMdTextArea.parent(),
      jqElement: this.introMdTextArea,
    })
  }

  initialize() {
    $('#id_comment_vote_hide_limit').select2({
      minimumResultsForSearch: Infinity,
    })
    this.initSelectMenus()
    this.initTextAreas()
  }
}

export function init(options) {
  const settingsPage = new Instance(options)
  settingsPage.initialize()
  return settingsPage
}
