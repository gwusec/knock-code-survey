# Templates and Bootstrap

Templates are used to render the HTML of a page. Ther eis a built in Django
language for templates that you can review here:
https://docs.djangoproject.com/en/2.0/ref/templates/builtins/

Additionally, to make CSS styling simpler, I've used bootstrap to do the
styling. You can see the bootstrap documenation here:
https://getbootstrap.com/docs/4.1/getting-started/introduction/


## Typical Page Template

A typical page loads a header template and the main page, as well as the
bootstrap CSS. For example

```
<!DOCTYPE html>
<html lang="en">

    <head>
        {% load static %}
        {% include "bootstrap_header.html" %}
    </head>
    
    <body>
        <div class="container-fluid">

            {% include "jumbo_header_no_opt_out.html" %}
            
        </div>
        <div class="container-fluid">
            <div class="w-auto shadow-lg p-3 mb-5 bg-white rounded">
        <p>
            We are conducting an academic survey about user chosen PINs, and you
            will be asked to complete a survey that will ask you to generate a
            number of PINs under different conditions. You will be <b>compensated $1.25</b> for your work. We have
            found that it takes aproximately <b> 10 minutes on average </b> to
            complete this HIT.
        </p>
```

First the `{% load static %}` indicates to use static loading, this is not
template HTML text. The `{% include "boostrap_header.html" %} is another
template containing the header loads:

```
{% load static %}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{% static 'survey/bootstrap.min.css' %}">
```

This way we don't have to copy and paste all the time. Same is true for the
other `include`, which contains a template for the banner.

## Banner Templates

There are two types of banners, with an opt out and without an opt out option.

 * `jumbo_header_no_opt_out.html` : no opt out option
 * `jumbo_header_w_opt_out.html` : with an opt out option

## Form Templates

Forms are more complicated as there are built in Django tmeplates for rendering
form elements, such as radio buttons. I do not like how Django does this, so I
came up with a simple way to render the buttons nicer, and with boostrap
classes.

Take, for example, the relevant part of the template for the demographic questoins:

```
        <div class="container-fluid">
            <form action="/" method="post">{% csrf_token %}
                <ol>
                    <li> {% include "radio.html" with field=form.age %} </li>
                    <li> {% include "radio.html" with field=form.gender %} </li>
                    <li> {% include "radio.html" with field=form.handed %} </li>
                    <li> {% include "radio.html" with field=form.locale %} </li>
                </ol>
                <input class="btn btn-outline-primary" type="submit" value="Submit" >
            </form>
        </div>
```

Each of these includes, takes a field of the form, eg., a question about age,
and sets that in a sub template. The `radio.html` template can then render that
question/field nicely with boostrap, with the label and each of the options
properly wrapped in the correct div class.

```
<strong> {{field.label}} </strong>
{% for opt in field %}
<div class="form-check">
    {{opt.tag}}
    <label class="form-check-label" for="{{opt.id_for_label}}">
        {{ opt.choice_label}}
    </label>
</div>
{% endfor %}
<br>
```

The form object are defined in `forms.py`



