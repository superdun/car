/**
 * Numeric stepper
 * @version 1.3.1
 * @namespace numStepper
 *
 * @param {Object} [options] - Custom options object
 * @param {Number} [options.steps=1] - Number of steps to increment/decrement input value
 * @param {Number} [options.minValue=1] - Minimum input value
 * @param {Number} [options.maxValue=null] - Maximum input value
 * @param {Boolean} [options.floatingPoint=false] - Allow floating point numbers
 * @param {String} [options.theme=default] -
 * @param {String} [options.inputWidth=null] -
 * @param {Object} [options.classes] - Component HTML class names object
 * @param {String} [options.classes.root='num-spinner'] - Component block
 * @param {String} [options.classes.input='num-spinner__input'] - Component input element
 * @param {String} [options.classes.input='num-spinner__unit'] - Component unit element
 * @param {String} [options.classes.btn='num-spinner__btn'] - Component button element
 * @param {String} [options.classes.btnInc='num-spinner__btn--increment'] - Component button element increment modification
 * @param {String} [options.classes.btnDec='num-spinner__btn--decrement'] - Component button element decrement modification
 *
 * @example /// Init without options
 * $( '.js-someclass' ).numStepper();
 * @example /// Init with options
 * $( '.js-differentclass' ).numStepper({
 *   steps: 10,
 *   minValue: 0,
 *   maxValue: 100
 * });
 */
(function( $, window, document, undefined ) {
	/// Create the defaults once
	var pluginName = 'numStepper';
	var defaults = {
		steps: 1,
		minValue: 1,
		maxValue: null,
		floatingPoint: false,
		unit: null,
		theme: 'default',
		inputWidth: null,
		classes: {
			root: 'numstepper',
			input: 'numstepper__input',
			inputUnitMod: 'numstepper__input--unit',
			unit: 'numstepper__unit',
			btn: 'numstepper__btn',
			btnInc: 'numstepper__btn--increment',
			btnDec: 'numstepper__btn--decrement'
		}
	};

	/// The actual plugin constructor
	function Plugin( element, options ) {
		this.element = element;
		this.options = $.extend( {}, defaults, options, $(this.element).data() );

		this._defaults = defaults;
		this._name = pluginName;

		this._init();
	}

	Plugin.prototype = {
		/**
		 * Initialization
		 * @function
		 * @public
		 * @memberof numStepper
		 */
		_init: function() {
			this._config();
			this._bindEvents();
		},

		/**
		 * Configures all internal variables, creates additional DOM elements, et cetera
		 * @function
		 * @private
		 * @memberof numStepper
		 */
		_config: function() {
			var attrMin, attrMax;
			var op = this.options;
			var cl = op.classes;

			this.isFirstRun = true;
			this.hasUnit = op.unit ? true : false;

			this.$root = $(this.element);
			this.$input = this.$root.find( 'input' );

			this.$root.addClass( cl.root + ' ' + cl.root + '--' + op.theme );
			this.$input.addClass( cl.input );

			this.$btnDecrement = $( '<button class="' + cl.btn + " " + cl.btnDec + '">&mdash;</button>' );
			this.$btnIncrement = $( '<button class="' + cl.btn + " " + cl.btnInc + '">+</button>' );

			this.$root.prepend( this.$btnDecrement );
			this.$root.append( this.$btnIncrement );

			this.$input.attr( 'type', 'number' );
			this.$input.attr( 'autocomplete', 'off' );

			attrMin = this.$input.attr( 'min' );
			attrMax = this.$input.attr( 'max' );

			if ( attrMin ) {
				if ( op.floatingPoint ) {
					op.minValue = parseFloat( attrMin.replace( ',', '.' ) );
				} else {
					op.minValue = parseInt( attrMin, 10 );
				}
			}

			if ( attrMax ) {
				if ( op.floatingPoint ) {
					op.maxValue = parseFloat( attrMax.replace( ',', '.' ) );
				} else {
					op.maxValue = parseInt( attrMax, 10 );
				}
			}

			this._setInputAttributes();

			if ( op.inputWidth ) {
				if ( typeof op.inputWidth === 'number' ) {
				    op.inputWidth += 'rem';
				}
				this.$input.css({ 'width' : op.inputWidth });
			}

			if ( this.hasUnit ) {
				this.$input.addClass( cl.inputUnitMod );
				this.$unit = $( '<div class="' + cl.unit + '">&nbsp;' + op.unit + '</div>' );
				this.$unit.insertAfter( this.$input );
				var unitWidth = this.$unit.outerWidth();
				this.$input.css({
					'text-align' : 'right',
					'width' : this.$input.outerWidth() + unitWidth + 'px',
					'padding-right' : unitWidth + 'px'
				});
				this.$unit.css({ 'margin-left' : unitWidth * -1 + 'px'});
			}

			if ( op.floatingPoint ) {
				/// Allow: Backspace (8), Delete (46), Tab (9), Escape (27), Enter (13), Decimal Point (110),
				/// Period (190), Comma (188), Dash (189), Subtract (109)
				this.keyCodes = [ 8, 46, 9, 27, 13, 110, 190, 188, 189, 109 ];
			} else {
				/// Allow: Backspace (8), Delete (46), Tab (9), Escape (27), Enter (13)
			 	this.keyCodes = [ 8, 46, 9, 27, 13 ];
			}

			this.value = null;
			this.valueOld = null;

			this._getValue();

			if ( !this.value ) {
				if ( op.minValue ) {
					this.value = op.minValue;
				} else {
					this.value = 0;
				}
				this.valueOld = this.value;
			}

			this._setValue();
		},

		/**
		 * Binds all event listeners
		 * @function
		 * @private
		 * @memberof numStepper
		 */
		_bindEvents: function() {
			var self = this;
			var op = this.options;
			var cl = op.classes;

			this.$root.off(
				'click change keydown'
			).on( 'click', '.'+ cl.btnDec, function(event) {
				event.preventDefault();
				self._setValue( 'dec' );
			}).on( 'click', '.'+ cl.btnInc, function(event) {
				event.preventDefault();
				self._setValue( 'inc' );
			}).on( 'change keydown', '.'+ cl.input, function(event) {
				switch ( event.type ) {
					case 'change':
						self._getValue();
						self._setValue( 'auto' );
						break;
					case 'keydown':
						/// Allow: Up (38), Add (107)
						if ( event.which == 38 || event.which == 107 ) {
							event.preventDefault();
							self._setValue( 'inc' );
							return;
						}
						/// Allow: Down (40), Subtract (109)
						if ( event.which == 40 || event.which == 109 ) {
							event.preventDefault();
							self._setValue( 'dec' );
							return;
						}
						/// Allow
						if (
							$.inArray( event.which, self.keyCodes ) !== -1 ||
							/// Allow: Ctrl/cmd + A
							( event.which == 65 && ( event.ctrlKey === true || event.metaKey === true ) ) ||
							/// Allow: Ctrl/cmd + C
							( event.which == 67 && ( event.ctrlKey === true || event.metaKey === true ) ) ||
							/// Allow: Ctrl/cmd + X
							( event.which == 88 && ( event.ctrlKey === true || event.metaKey === true ) ) ||
							/// Allow: End (35), Home (36), Left (37), Right (39)
							( event.which >= 35 && event.which <= 39 )
						) {
							/// Let it happen, don't do anything
							return;
						}

						/// Ensure that it is a number and stop the keypress
						if (
							( event.shiftKey || ( event.which < 48 || event.which > 57 ) ) &&
							( event.which < 96 || event.which > 105)
						) {
							event.preventDefault();
						}
						break;
					default:
						return;
				}
			});

			if ( this.hasUnit ) {
				this.$root.on( 'click', '.'+ cl.unit, function(event) {
					event.preventDefault();
					event.stopPropagation();
					self.$input.focus();
				});
			}
		},

		/**
		 * xxxxxx
		 * @function
		 * @private
		 * @memberof numStepper
		 */
		_setInputAttributes: function() {
			var op = this.options;

			if ( typeof op.minValue === 'number' ) { this.$input.attr( 'min', op.minValue ); }
			if ( typeof op.maxValue === 'number' ) { this.$input.attr( 'max', op.maxValue ); }
		},

		/**
		 * Gets the input element value
		 * @function
		 * @private
		 * @memberof numStepper
		 */
		_getValue: function() {
			var op = this.options

			this.valueOld = this.value;

			if ( op.floatingPoint ) {
				this.value = parseFloat( this.$input.val().replace( ',', '.' ) );
			} else {
				this.value = parseInt( this.$input.val(), 10 );
			}

			if ( isNaN( this.value ) ) {
				this.value = this.valueOld;
			}
		},

		/**
		 * Increases or decreases the value and sets the new value
		 * @function
		 * @private
		 * @memberof numStepper
		 *
		 * @param {String} mode - [ dec | inc | auto ]
		 * @fires change.numstep
		 */
		_setValue: function( mode ) {
			var op = this.options;

			switch ( mode ) {
				case 'dec':
					this.valueOld = this.value;
					this.value -= op.steps;
					break;
				case 'inc':
					this.valueOld = this.value;
					this.value += op.steps;
					break;
				case 'auto':
				default:
					if ( this.value < this.valueOld ) {
						mode = 'dec';
					} else if ( this.value > this.valueOld ) {
						mode = 'inc';
					} else {
						mode = null;
					}
			}

			this._checkMinMax();

			if ( op.floatingPoint ) {
				this.$input.val( this.value.toLocaleString() );
			} else {
				this.$input.val( this.value );
			}

			if ( this.isFirstRun || this.value !== this.valueOld ) {
				this.isFirstRun = false;

				/**
				 * Triggers numeric spinner change event on root element.
				 * The mode (inc/dec), value and valueOld are passed to the event handling function as argument after the event object.
				 * @event change.numstep
				 *
				 * @returns {Object} eventData
				 * @returns {String} mode
				 * @returns {Number} value
				 * @returns {Number} valueOld
				 */
				this.$root.trigger( 'change.numstep', [ mode, this.value, this.valueOld ] );
			}
		},

		/**
		 * Checks for min/max values and disables/enables buttons
		 * @function
		 * @private
		 * @memberof numStepper
		 */
		_checkMinMax: function() {
			var op = this.options;

			/// Alle Buttons aktivieren
			this.$btnDecrement.attr( 'disabled', false );
			this.$btnIncrement.attr( 'disabled', false );

			/// Wenn min gesetzt und value kleiner gleich min
			if ( op.minValue && this.value <= op.minValue ) {
				this.value = op.minValue;
				this.$btnDecrement.attr( 'disabled', true );
			}

			/// Wenn max gesetzt und value groesser gleich max
			if ( op.maxValue && this.value >= op.maxValue ) {
				this.value = op.maxValue;
				this.$btnIncrement.attr( 'disabled', true );
			}
		},

		/**
		 * Sets any option by its name after initialization
		 * @function
		 * @public
		 * @memberof numStepper
		 *
		 * @param {String} option - Option name
		 * @param {String} option - Option value
		 * @param {Boolean} [trigger] - Trigger change.numstep event on root element
		 *
		 * @example $(element).numericSpinner( 'setOption', 'maxValue', 15, true );
		 */
		setOption: function( option, value, trigger ) {
			this.options[option] = value;

			this._setInputAttributes();

			if ( trigger ) {
				this.$input.trigger( 'change' );
			}
		},

		/**
		 * Get any option by its name
		 * @function
		 * @private
		 * @memberof numStepper
		 *
		 * @param {String} option
		 * @returns {*}
		 *
		 * @example $(element).numericSpinner( 'getOption', 'maxValue' );
		 */
		/*
		getOption: function( option ) {
			return this.options[option];
		},
		*/

		/**
		 * Destroys the plugin
		 * @function
		 * @public
		 * @memberof numStepper
		 *
		 * @example $(element).numericSpinner( 'destroy' );
		 */
		destroy: function() {
			this.$input.off();
			this.$btnDecrement.remove();
			this.$btnIncrement.remove();
			this.$root.removeClass( this.options.classes.root );
			this.$input.removeClass( this.options.classes.input );
			$.removeData( this.element );
		}
	};

	/**
	 * Logs console errors
	 * @function
	 * @private
	 * @memberof numericSpinner
	 */
	var _logError = function( message ) {
		if ( window.console ) {
			window.console.error( message );
		}
	};

	$.fn[pluginName] = function( options ) {
		if ( typeof options === 'string' ) {
			var args = Array.prototype.slice.call( arguments, 1 );

			this.each(function() {
				var instance = $.data( this, 'plugin_' + pluginName );

				if ( !instance ) {
					_logError(
						'Cannot call methods on '+ pluginName +' prior to initialization;' +
						'attempted to call method "'+ options +'"'
					);
					return;
				}

				if ( !$.isFunction( instance[ options ] ) || options.charAt(0) === "_" ) {
					_logError( 'No such method "'+ options +'" for '+ pluginName +' instance' );
					return;
				}

				instance[ options ].apply( instance, args );
			});
		} else {
			this.each( function() {
				if ( !$.data( this, 'plugin_' + pluginName ) ) {
					$.data( this, 'plugin_' + pluginName, new Plugin( this, options ) );
				}
				/*
				var instance = $.data( this, 'plugin_' + pluginName );

				if ( instance ) {
					instance.destroy();
					instance._init();
				} else {
					$.data( this, 'plugin_' + pluginName, new Plugin( this, options ) );
				}
				*/
			});
		}

		return this;
	};
})( jQuery, window, document );


