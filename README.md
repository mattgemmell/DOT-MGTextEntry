# DOT-MGTextEntry

by [Matt Gemmell](http://mattgemmell.com/)


## What is it?

It's a text-entry menu plugin for the Raspberry Pi's Display-O-Tron.


## What are its requirements?

- Any Raspberry Pi
- Any Display-O-Tron (either HAT or 3000)
- Pimoroni's [Display-O-Tron code and examples](https://github.com/pimoroni/dot3k/)


## What does it do?

It lets you enter text on the Display-O-Tron (DOT), using either the touch-controls or the joystick, depending on which version of the DOT you have.

It's basically a games-console-like text-entry system, with a grid of letters and numbers, and a cursor to move around and select them for entry. Here it is in action:

![Display-O-Tron Text Entry on Raspberry Pi](https://c2.staticflickr.com/2/1704/25021496493_aca0d6de99_c.jpg)

And here's my original design plan for it:

![Display-O-Tron Text Entry plan](https://c2.staticflickr.com/2/1565/25529423232_1f80472949_c.jpg)

(Here's [a larger version](https://www.flickr.com/photos/mattgemmell/25529423232/).)

You move around with the directional controls, enter characters into the input field with the Select touch-button (or pressing the joystick), and if you have a DOT HAT, you can use the Cancel button as a Delete key.

The keyboard can be toggled into uppercase, lowercase, or symbols mode. There are also options to quit the editor, or accept what you've typed so far (it'll be returned to the parent menu system, for use by whatever menu used this plugin as its input-handler).

That's about it.


## How do I use it?

Use it as a plugin for your existing menus, using Pimoroni's menu API. You can also use it on its own, I suppose. See the included `text-test.py` file.


## Who made it?

Matt Gemmell (that's me).

- My website is at [mattgemmell.com](http://mattgemmell.com)

- I'm on Twitter as [@mattgemmell](http://twitter.com/mattgemmell)

- This code is on github at [github.com/mattgemmell/DOT-MGTextEntry](http://github.com/mattgemmell/DOT-MGTextEntry)


## What license is the code released under?

The [MIT license](http://choosealicense.com/licenses/mit/).

If you need a difference license, feel free to ask. I'm flexible about this.


## Why did you make it?

It's my first ever Raspberry Pi-related coding project. Mostly for fun.


## Can you provide support?

Nope. If you find a bug, please fix it and submit a pull request via github.


## I have a feature request

Feel free to [create an issue](https://github.com/mattgemmell/DOT-MGTextEntry/issues) with your idea.


## How can I thank you?

You can:

- [Support my writing](http://mattgemmell.com/support-me/).

- Check out [my Amazon wishlist](http://www.amazon.co.uk/registry/wishlist/1BGIQ6Z8GT06F).

- Say thanks [on Twitter](http://twitter.com/mattgemmell), I suppose.
