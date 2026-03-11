# Architecture decision record - CSS Frameworks

This document will cover the process of choosing between two potential CSS Frameworks: Bootstrap (used in the previous 'rango' project) and Tailwind (heavily inspired templates used in the design specification). 

We initially considered using bootstrap due to the range of pre-built components and the fact we had some documentation on its use through Rango. However, there are a number of components that we would need to create, essentially from scratch. And, while customization of existing components can be easier in Bootstrap, creating components like chips for categories, the larger search bar and the cards view would be more difficult than using a heavily customizable framework like Tailwind.

Upon some research, we did find a fork of a UI platform known as shadcn, which provides premade components for tailwind css in the django platform as well. Shadcn-django is also a platform that takes components as individual imports per page, meaning we can only pull in the aspects we need for efficiency. Bootstrap would force us to take in all components, even those we don't need.

Shadcn-django also has syntax of HTML at its core, meaning it is reliable and useful. For the components it does not have, though, including the components chip toggle buttons within the _control_strip, we can make these ourselves, using existing components as a base.

## Our plan

* Django: **Version 6.0.3 - latest version with newest features
* Python: **3.12 - minimum required version for the UI layer of Tailwind CSS.
