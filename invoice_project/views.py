from django.shortcuts import render

def invoice_form_view(request):
    return render(request, "invoice_form.html")