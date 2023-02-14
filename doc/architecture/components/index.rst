.. _product-components:

******************
Product components
******************

In this part of the document, you learn about the second, medium, detail level of
the architecture of |UCS|. You learn about UCS product components that you face
directly when you use UCS. The product components typically act as entry points
for your tasks.

The description of the product components is for administrators and solution
architects. For software developers and system engineers it provides the context
for the architectural details to UCS. Make sure you are familiar with the
:ref:`concepts` behind UCS.

For architecture notation, this part of the document uses ArchiMate® 3.1, a
visual language with a set of default iconography for describing, analyzing, and
communicating many concerns of enterprise architectures. For more information
about how the document uses the notation, refer to
:ref:`architecture-notation-archimate`.

The following product components from :numref:`product-components-model`
introduce themselves in the order you most likely encounter them when you work
with UCS:

#. :ref:`component-portal`
#. :ref:`component-management-system`
#. :ref:`component-app-center`

..
   #. :ref:`component-file-print`
   #. :ref:`component-command-line`

.. _product-components-model:

.. figure:: /images/product-components.*
   :alt: UCS Product components with UCS Management System, UCS Portal, App
         Center, File and Print, and Command-line

   User facing product components of UCS

.. hint::

   The section is work in progress. Later updates of the document explain the
   concepts *Command line* and *File and print*. For the sake of completeness
   :numref:`product-components-model` already shows them.

.. TODO : Remove or change hint, once Command line and File and print are
   explained.

.. toctree::
   :maxdepth: 2
   :hidden:

   portal
   management-system
   app-center
