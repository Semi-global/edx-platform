/**
 * A search field that works in concert with a paginated collection. When the user
 * performs a search, the collection's search string will be updated and then the
 * collection will be refreshed to show the first page of results.
 */
;(function (define) {
    'use strict';

    define(['backbone', 'jquery', 'underscore', 'text!common/templates/components/search-field.underscore'],
        function (Backbone, $, _, searchFieldTemplate) {
            return Backbone.View.extend({

                events: {
                    'submit .search-form': 'performSearch',
                    'blur .search-form': 'onFocusOut',
                    'keyup .search-field': 'refreshState',
                    'click .action-clear': 'clearSearch'
                },

                initialize: function(options) {
                    this.type = options.type;
                    this.label = options.label;
                },

                refreshState: function() {
                    var searchField = this.$('.search-field'),
                        clearButton = this.$('.action-clear'),
                        searchString = $.trim(searchField.val());
                    if (searchString) {
                        clearButton.removeClass('is-hidden');
                    } else {
                        clearButton.addClass('is-hidden');
                    }
                },

                render: function() {
                    this.$el.html(_.template(searchFieldTemplate, {
                        type: this.type,
                        searchString: this.collection.searchString,
                        searchLabel: this.label
                    }));
                    this.refreshState();
                    return this;
                },

                onFocusOut: function(event) {
                    // If the focus is going anywhere but the clear search
                    // button then treat it as a request to search.
                    if (!$(event.relatedTarget).hasClass('action-clear')) {
                        this.performSearch(event);
                    }
                },

                performSearch: function(event) {
                    var searchField = this.$('.search-field'),
                        searchString = $.trim(searchField.val());
                    event.preventDefault();
                    this.collection.setSearchString(searchString);
                    return this.collection.refresh();
                },

                clearSearch: function(event) {
                    event.preventDefault();
                    this.$('.search-field').val('');
                    this.collection.setSearchString('');
                    this.refreshState();
                    return this.collection.refresh();
                }
            });
        });
}).call(this, define || RequireJS.define);
