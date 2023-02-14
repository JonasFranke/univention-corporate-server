.. _component-app-center:

App Center
==========

Univention App Center is one of the most important parts of |UCS|. It's
responsible for the lifecycle management of UCS components and third party
applications that add enterprise software to the UCS domain. The App Center
simplifies the installation and integration of software with UCS. In this
respect, the App Center is similar in principle to the app stores on mobile
platforms, with the difference that it applies to the server infrastructure.

Apps, short for applications, are the content in the App Center. Univention
offers components for UCS as apps. And third party vendors, so-called app
providers, offer software solutions as apps. Apps consist of software,
integration with UCS and metadata, such as texts and logos for presentation. A
central idea of the apps is the tight integration with UCS, especially the
integration with identity management.

Like many other product components, administrators interact with the App Center
either through the web based management system or a terminal as shown in
:numref:`component-app-center-architecture-component`.

.. _component-app-center-architecture-component:

.. figure:: /images/App-Center-architecture-component.*
   :width: 600 px

   Architecture overview of the App Center

Abstractly speaking, the application service *App Center* offers a web interface
through *HTTP/HTTPS* and a command line interface through *Terminal / SSH*.

The following list demarcates the App Center from its capabilities. The App
Center isn't:

* a tool to distribute software specific to customers or projects.

* a solution for every use case. It has limitations for example in large
  environments that require cluster or load balancing setups.

Think of the App Center as a global entity in the UCS domain. The App Center
addresses all UCS systems. Administrators can view and install any available
app.

This section provides information about the following aspects around the App
Center:

* :ref:`component-app-center-ecosystem-actors` in the context of the App Center
  ecosystem.

* :ref:`component-app-center-ecosystem-apps` for an overview of the content in
  the App Center.

* :ref:`component-app-center-infrastructure` around the App Center.

.. admonition:: Continue reading

   :ref:`services-app-center`
      for the next detail level with description of the ecosystem,
      infrastructure, and architecture of the App Center.

.. seealso::

   :ref:`software-appcenter`
      for information for administrators about the App Center in
      :cite:t:`ucs-manual`

   :external+uv-app-center:doc:`Univention App Center for App Providers <index>`
      for information about how to develop apps for Univention App Center in
      :cite:t:`ucs-app-center`


.. _component-app-center-purpose:

App Center purpose
------------------

.. index::
   single: app center; purpose
   pair: app center; benefits


Depending on the direction you look at the App Center, it has different purposes
and provides different benefits.

First, the App Center provides value to customers in terms of software
management:

* Maintained enterprise software integrated with |UCS| identity management. The
  existing integration reduces the effort for customers to maintain such an
  integration.

* Software lifecycle management with simplified installation and updating of
  software applications in a server infrastructure.

:numref:`component-app-center-purpose-model` shows the purposes of the App
Center for *Customers* and *App providers*.

.. _component-app-center-purpose-model:

.. figure:: /images/App-Center-purpose.*
   :width: 650 px

   Purpose of the App Center

Second, because the App Center is part of |UCS|, app providers benefit from a
good customer base and an enterprise platform with integrated identity
management. With integrated identity management at their fingertips, app
providers don't have to worry about identity management on their own and they
can rely on the offered interfaces such as LDAP, SAML and OpenID Connect.

.. TODO : Once the chapters about the authentication protocols exist, convert
   them to cross-references.


.. _component-app-center-ecosystem:

App Center ecosystem
--------------------

On the one hand, the App Center is a user-facing product component in |UCS|. The
:ref:`services-app-center` covers the architecture and technology in more
detail. On the other hand, the App Center is also an ecosystem with services,
various actors, content, and infrastructure.

This section provides an overview of the ecosystem.

.. _component-app-center-ecosystem-actors:

App Center actors
~~~~~~~~~~~~~~~~~

.. index::
   see: app center actors; app center roles

:numref:`component-app-center-actors` shows the actors involved in the
Univention App Center ecosystem. For the sake of brevity, the figure shows a
subset of the responsibilities.

.. _component-app-center-actors:

.. figure:: /images/App-Center-actors.*
   :width: 600 px

   Actors in the App Center ecosystem

.. _app-center-ecosystem-platform-maintainer:

App platform maintainer
"""""""""""""""""""""""

.. index::
   pair: app center roles; app platform maintainer

*Univention*, as the software provider for |UCS|, is the *App platform
maintainer* and as such is responsible for *Univention App Center*. For example,
Univention operates the infrastructure so that administrators can install
software through the App Center. An important task in the service for the *App
provider* is the *App provider support* during app on-boarding and app
maintenance.

.. _app-center-ecosystem-app-provider:

App provider
""""""""""""

.. index::
   pair: app center roles; app provider
   pair: app center roles; app maintainer
   pair: app center roles; app vendor

The next actor in the App Center ecosystem is the *App provider* in the
following specializations:

App maintainer
   The *App maintainer* doesn't own the software, but maintains the app with the
   software in the App Center.

   The App Center also contains open source apps. Organizations take on the role
   of the *App maintainer*. They don't own the open source software. They invest
   their knowledge of |UCS| and the software into an app, its integration with
   UCS, and the maintenance of the app for the benefit of customers and to
   promote open source software.

App vendor
   The *App vendor* owns the software. Organizations that own software and
   maintain their own app in Univention App Center act in both roles of *App
   vendor* and *App maintainer* at the same time.

.. _app-center-ecosystem-customer:

Customer
""""""""

.. index::
   pair: app center roles; customer
   pair: app center roles; user

The third actor is the customer in the role of the user. They use *Univention
App Center* with the associated services and apps to cover their software needs
for their business.

.. _component-app-center-ecosystem-apps:

App Center apps
~~~~~~~~~~~~~~~

.. index::
   single: app; integration
   single: app; metadata
   single: app; package based app
   single: app; docker based app
   single: app; software application
   single: software application; app
   single: app; single container app
   single: app; multi container app
   single: docker; single container app
   single: docker; multi container app
   pair: app center; app

The content in the App Center are apps. At the technology level an *App Center
app* consists of the parts shown in
:numref:`component-app-center-apps-aggregation`.

.. _component-app-center-apps-aggregation:

.. figure:: /images/App-Center-apps-1.*
   :width: 500 px

   Parts of an app

Software application for app
   *Software application for app* is the software itself, the binary artifact as
   provided by the vendor.

App integration
   *App integration* includes scripts and software tailored to the integration
   needs of the software application and |UCS|. They take care of the proper
   setup so that the app is ideally ready to use after installation. For
   example, the integration may consist of:

   * Setup for single sign-on configuration between the software application and
     |UCS|.

   * Configuration to set up the web server.

   * Script to populate a database with the database schema and required data.

   * Environment setup for configuring the software application.

App metadata
   *App metadata* is the content responsible for properly presenting the app to
   the user in the App Center. It includes name, description, logo, and contact
   information for the app provider.

The App Center recognizes the *Software application for app* in the form in
which the vendor distributes the binary artifact, as shown in
:numref:`component-app-center-apps`.

.. _component-app-center-apps:

.. figure:: /images/App-Center-apps-2.*
   :width: 350 px

   Kinds of software distribution for the App Center

Package based app
   *Package based app* refers to software distributed using :ref:`Debian
   packages <positioning-packages>`. Apps that extend the core capabilities of
   UCS use Debian packages for software distribution. The App Center installs
   the packages from dedicated repositories per app and handles the repository
   configuration.

Docker based app
   *Docker based app* refers to software distributed through Docker images, a
   data format for containerized software. Docker based apps decouple the
   software runtime from the underlying UCS operating system and reduce the
   complexity of app maintenance for app providers.

   .. important::

      The App Center prefers Docker based apps over package based apps.

Finally, a *Docker based app* can be either a *Single container app* or a *Multi
container app*, as shown in :numref:`component-app-center-docker-apps`.

.. _component-app-center-docker-apps:

.. figure:: /images/App-Center-apps-3.*
   :width: 350 px

   Kinds of Docker apps

Single container app
   Individual single container apps consist of a Docker image. UCS uses the
   Docker engine to run them.

Multi container app
   Multi container apps, on the other hand, consist of more than one Docker
   image. UCS uses `Docker compose <docker-compose_>`_ and the Docker engine to
   run them. App providers that offer their app as multi container app often
   provide the required parts as micro services for better decoupling and
   dependency control. They also typically offer this type of deployment anyway,
   independent of the App Center.

:numref:`component-app-center-apps-model` shows the overall model, its parts and
what an app consists of. On the application level the App Center differentiates
an *App* into *Package based app* and *Docker based app* and handles both.

.. _component-app-center-apps-model:

.. figure:: /images/App-Center-apps.*
   :width: 600 px

   Apps as content in the App Center ecosystem

.. _component-app-center-infrastructure:

App Center infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~

.. index::
   single: app center roles; app developer
   single: app center roles; user
   single: app center roles; app provider
   single: app center roles; administrator
   pair: app catalog; app center
   pair: app center; provider portal
   see: app provider portal; provider portal
   pair: app center; repository

The App Center requires a dedicated infrastructure consisting of several
elements to function properly.
:numref:`component-app-center-infrastructure-model` shows the infrastructure,
and the description of each element follows.

.. _component-app-center-infrastructure-model:

.. figure:: /images/App-Center-infrastructure.*
   :width: 650 px

   App Center infrastructure model

App developer
   An *App developer* is a software developer who is responsible for creating
   and maintaining an app. The *App developer* is part of the
   :ref:`app-center-ecosystem-app-provider`.

App Provider portal
   The *App Provider portal* is the entry point for app developers who create
   and maintain an app in the App Center. It handles authentication and access
   rights to the app definitions for app developers. And, it uploads the app
   software to the *App Center repository*.

   Technically, the *App Provider portal* is a :ref:`UMC module
   <services-umc-modules>` running on UCS.

App Center repository
   The *App Center repository* is the central repository for the apps. UCS
   systems connect to the *App Center repository* to load the app metadata for
   presentation and to download the app for installation on a UCS system.

   The *App Center repository* consists of the following parts:

   * *Production App Center repository* is the location where all UCS systems
     download the apps. It contains the publicly available apps.

   * *App Center Docker registry* is the location for the Docker images of Docker
     based apps.

   * *Test App Center repository* is the location for apps under development.
     Only app developers use it during app development. After an app release
     completes, the app appears in the *Production App Center repository*.

App Catalog
   The *App Catalog* is part of the Univention website and provides an overview
   of the available apps and their descriptions. It's a representation of the
   app metadata for user information purposes. The *App Catalog* loads the data
   from the *App Center repository* server.

App Center
   In the context of :numref:`component-app-center-infrastructure-model`, the
   term *App Center* refers to everything on a local UCS system that makes up
   the App Center. The *App Center* loads the app information from the *App
   Center repository* over the *Internet*.

   For the architecture of the *App Center*, refer to
   :ref:`services-app-center`.

Administrator
   The *Administrator* is the primary *User* role that interacts with the *App
   Center* on a UCS system. The *Administrator* has the user rights to install,
   update, and remove apps on a UCS system.

.. seealso::

   :ref:`software-appcenter`
      for more information for administrators about how to use the App
      Center in :cite:t:`ucs-manual`.

   :external+uv-app-center:doc:`Univention App Center for App Providers <index>`
      for more information for app developers about how to develop apps for
      Univention App Center in :cite:t:`ucs-app-center`

   `App Catalog <https://www.univention.com/products/univention-app-center/app-catalog/>`_ on the Univention website
      for an overview about available apps in the App Center.

