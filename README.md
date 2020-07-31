# Badminton-App #
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/Adspectus/Badminton-App?style=flat-square&label=Version)](https://github.com/Adspectus/Badminton-App/releases)
[![GitHub issues](https://img.shields.io/github/issues/Adspectus/Badminton-App?style=flat-square&label=Issues)](https://github.com/Adspectus/Badminton-App/issues)
[![GitHub license](https://img.shields.io/github/license/Adspectus/Badminton-App?style=flat-square&label=License)](https://github.com/Adspectus/Badminton-App/blob/master/LICENSE)
[![Perl version](https://img.shields.io/static/v1?label=Perl&message=5&color=yellow&style=flat-square)](https://www.perl.org/)

[Deutsch](LIESMICH.md)

Web app for the management of training dates for a badminton group

## Genesis

This app has been created to ease the management of training dates for the members of a badminton group and to match the court rental charge accordingly. Because of fluctuation it often has been unpredictable how many participants would show up to the weekly training session. Sometimes this resulted in the unwanted situation that either too many courts have been booked (and had to be paid) or too many participants showed up on insufficient courts.

Since it is possible to cancel pre-booked courts at no charge within a period prescribed by the sports center, the target was to make this deadline mandatory and to impose a fine for late calls.

As a consequence, commitments and cancellations of individual participations should be as easy and reproducible as possible. Sending mails and messages back and forth however did not lead to any improvement because this turned out to be a mess. Especially the task of compiling these messages and book or cancel courts in due time is a sisyphean task for the one to be in charge.

Thus, the main requirement has been to provide a simple and effective possibility for the participants to express their binding commitment or cancellation of participation in forthcoming training sessions. In the course of time many other requirements has been added and implemented, amongst others:

* Password protected account for each participant to ensure liability and traceability.
* Possibility for non-members to participate as guest.
* Avoidance of non-active members.
* Independent of device.
* Reports of participation and costs.

## Getting Started

The Badminton application is a "web app" which is just a website but with a responsive design to be used on smaller devices. The data is stored in a MySQL database. This architecture does not allow for an offline usage scenario, i.e. you need always a connection to the internet when working with the app.

### Prerequisites

* Webserver, i.e. Apache, with CGI (activated cgid module)
* *Perl* 5
* MySQL with activated event scheduler
* For sending mails: external SMTP gateway

### Installation

Given the prerequisites above, the following installation steps must be executed:

1. Clone this repository to your computer.
2. Create a configuration for your webserver/virtual host.

   The docroot must be pointed to the `htdocs` directory. The file [badminton.conf](badminton.conf) contains an example configuration for the Apache webserver (including http->https redirection). Note that you need to replace the placeholders &lt;IP&gt;, &lt;DOMAIN&gt;, &lt;INSTALLDIR&gt;, &lt;CERTFILE&gt;, and &lt;KEYFILE&gt; with real values. &lt;INSTALLDIR&gt; is the directory from step 1.
3. Install required *Perl* modules.

   Any standard installation of *Perl* already contains most of the required modules. To find which modules are missing, you can use the script `CheckEnvironment.pl` which will be invoked by executing the `CheckEnvironment.sh` shell script. Every module which is missing will throw an error message. Missing modules could be installed either by the software installation of your operating system or from [CPAN](https://www.cpan.org/). An exception to this are the modules by the author `Website::Template` and `Website::Framework::Bootstrap` which need to be installed by cloning [this repository](https://github.com/Adspectus/WebSite).

   Example: On a Debian 9/Ubuntu 18.04 based system the following modules could be installed by apt:

   Module | Package
   --- | ---
   `Date::Calc` | `libdate-calc-perl`
   `Email::MessageID` | `libemail-messageid-perl`
   `Email::Sender::Simple` | `libemail-sender-perl`
   `CGI::Session` | `libcgi-session-perl`
   `Config::Merge` | `libconfig-merge-perl`
   `Text::Markdown::Discount` | `libtext-markdown-discount-perl`
   `Module::Find` | `libmodule-find-perl`

   Only the module `CGI::Session::Auth` has to be installed directly from [CPAN](https://www.cpan.org/).

4. Create a database and an *initial database configuration*.
   1. Import the [badminton.sql](badminton.sql) script to create the database. If you would like to use a different name of the database instead of `badminton` you need to change this in the first 2 lines of the script.
   2. Create the database user and the initial configuration with the [configure.sql](configure.sql) script. Change the variables in the head of the file to your needs:

    ```sql
      SET @db_host       = '';      -- Hostname/IP of database server
      SET @db_name       = '';      -- Name of database (must match the name used in badminton.sql!)
      SET @db_user       = '';      -- MySQL user for database connection
      SET @db_pass       = '';      -- Password of MySQL user for database connection

      SET @my_user       = '';      -- The username of the first user with superuser privileges for the app
      SET @my_pass       = '';      -- The password of the first user
      SET @my_fname      = '';      -- The firstname of the first user
      SET @my_lname      = '';      -- The lastname of the first user
      SET @my_email      = '';      -- The emailaddress of the first user

      SET @matchday      = '3';     -- The day of the week for the training (Monday = 0, Tuesday = 1, etc.)
      SET @matchtime     = '19:30'; -- The time when the training starts (HH:MM)
      SET @deadline      = '91800'; -- The deadline for voting in seconds before the training starts
      SET @courts        = '9';     -- The number of courts which will be usually booked
      SET @nextdays      = '8';     -- The number of next training dates shown in user interface
      SET @fee           = '0';     -- The fee each player has to pay (per year)
      SET @guestcontrib  = '5';     -- The fee a guest has to pay (per training)
      SET @latefreeshots = '3';     -- The number of late votings without sanction
      SET @latepenalty   = '5';     -- The fee for every late voting (minus free shots)
      SET @pricepercourt = '12';    -- The price for each court
     ```
   The `configure.sql` file will only be needed for the initial configuration of the database and can be deleted or archived afterwards.

### Configuration

Given the prerequisites and the installation above, you will need to *configure the application*. This is done by a bunch of YAML files in the `config` subdirectory. The application will read all *.yml files in this directory and merge these to one configuration. The existing files in this directory already contain the necessary parameters, however some parameters are left empty. Either fill in or overwrite the values in these files or create a new file `Local.yml` by which you can overwrite all existing values. This is recommended and described here.

The file `Local.yml` could appear like this:

```yaml
Environment: DEV
UI:
    Organisation: Sportfreunde Schiller
    Title: SF Schiller
DB:
    User: sfs_badminton
    Password: geheim
Email:
    Host: smtp.example.com
    User: max@sfs.de
    Password: geheim
    FromName: Sportfreunde Schiller Badminton-App
    FromMail: badminton-app@sfs.de
    ToName: Max Mustermann
    ToMail: max@sfs.de
```

Description of parameters:

#### `Environment`

For non-productive environment use `DEV` or `TEST` here. Default: `PROD`

#### `UI`

##### `Organisation`

Meaningful name of your organisation/group. Default: `Badminton Sportgruppe`

##### `Title`

Short name of your organisation/group. Default: `Badminton`

##### `LoginVarPrefix`

Prefix for the login form fields `username` and `password`. Default: `bm_`

#### `DB`

##### `Host`

Hostname/IP of database server. Default: `localhost`

##### `Database`

Name of database created in step 4.i of the installation. Default: `badminton`

##### `User`

Name of MySQL user for database connection created in step 4.ii of the installation. Default: (empty)

##### `Password`

Password of MySQL user for database connection created in step 4.ii of the installation. Default: (empty)

#### `Email`

##### `Host`

Hostname/IP of your SMTP server to be used for sending emails. Default: (empty)

##### `SSL`

Use SSL for the connection to SMTP server. Default: `1` (Yes)

##### `User`

Username for SMTP server connection. Default: (empty)

##### `Password`

Password of user for SMTP server connection. Default: (empty)

##### `FromName`

The name of the sender for mails being sent by the app. Default: `Badminton-App`

##### `FromMail`

The email address of the sender for mails being sent by the app. Default: (empty)

##### `ToName`

Name of recipient for mails being sent by the app if no other recipient used (i.e. in case of testing). Most likely the superuser. Default: (empty)

##### `ToMail`

Email address of recipient for mails being sent by the app if no other recipient used (i.e. in case of testing). Most likely the superuser. Default: (empty)

## Usage

## License

[GNU General Public License v3.0](LICENSE)

## Acknowledgements

Created with [Perl](http://www.perl.org/), [MySQL](http://dev.mysql.com/), [jQuery](http://jquery.com/), [Bootstrap](http://getbootstrap.com/), [Glyphicons](http://glyphicons.com/), and [Markdown](http://daringfireball.net/projects/markdown/).

Icons made by Freepik from [www.flaticon.com](http://www.flaticon.com/) is licensed by [CC BY 3.0](http://creativecommons.org/licenses/by/3.0/ "Creative Commons BY 3.0").
