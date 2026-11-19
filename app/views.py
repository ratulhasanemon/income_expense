from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Transaction, CATEGORY_CHOICES
from datetime import date, timedelta
import json


def index(request):
    # Filter
    filter_type = request.GET.get('type', '')
    filter_month = request.GET.get('month', '')

    transactions = Transaction.objects.all()

    if filter_type:
        transactions = transactions.filter(type=filter_type)
    if filter_month:
        year, month = filter_month.split('-')
        transactions = transactions.filter(date__year=year, date__month=month)

    # Totals
    all_tx = Transaction.objects.all()
    total_income = all_tx.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0
    total_expense = all_tx.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0
    net_balance = total_income - total_expense

    # Monthly chart data (last 6 months)
    chart_labels = []
    chart_income = []
    chart_expense = []
    today = date.today()
    for i in range(5, -1, -1):
        d = today.replace(day=1) - timedelta(days=i * 28)
        label = d.strftime('%b %Y')
        inc = Transaction.objects.filter(
            type='income', date__year=d.year, date__month=d.month
        ).aggregate(s=Sum('amount'))['s'] or 0
        exp = Transaction.objects.filter(
            type='expense', date__year=d.year, date__month=d.month
        ).aggregate(s=Sum('amount'))['s'] or 0
        chart_labels.append(label)
        chart_income.append(float(inc))
        chart_expense.append(float(exp))

    # Category breakdown for expenses
    expense_categories = {}
    for tx in Transaction.objects.filter(type='expense'):
        cat = tx.get_category_display() or 'Other'
        expense_categories[cat] = expense_categories.get(cat, 0) + float(tx.amount)

    income_categories = [c for c in CATEGORY_CHOICES if 'other_expense' not in c[0] and c[0] in [
        'salary', 'freelance', 'business', 'investment', 'gift', 'other_income']]
    expense_category_list = [c for c in CATEGORY_CHOICES if c[0] not in [
        'salary', 'freelance', 'business', 'investment', 'gift', 'other_income']]

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'chart_labels': json.dumps(chart_labels),
        'chart_income': json.dumps(chart_income),
        'chart_expense': json.dumps(chart_expense),
        'expense_categories': json.dumps(expense_categories),
        'income_categories': income_categories,
        'expense_category_list': expense_category_list,
        'filter_type': filter_type,
        'filter_month': filter_month,
        'today': today.strftime('%Y-%m-%d'),
    }
    return render(request, 'index.html', context)


def add_transaction(request):
    if request.method == 'POST':
        tx_type = request.POST.get('type')
        title = request.POST.get('title', '').strip()
        amount = request.POST.get('amount')
        category = request.POST.get('category', '')
        note = request.POST.get('note', '')
        tx_date = request.POST.get('date') or date.today()

        if title and amount:
            Transaction.objects.create(
                type=tx_type,
                title=title,
                amount=amount,
                category=category,
                note=note,
                date=tx_date,
            )
            messages.success(request, f'{"Income" if tx_type == "income" else "Expense"} added successfully!')
        else:
            messages.error(request, 'Title and amount are required.')
    return redirect('index')


def delete_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    tx.delete()
    messages.success(request, 'Transaction deleted.')
    return redirect('index')