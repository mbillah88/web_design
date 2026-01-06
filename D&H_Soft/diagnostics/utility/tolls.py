
def calculate_commissions_for_visit(visit):
    commissions = []

    for advice in visit.testadvice_set.all():
        group = advice.group
        price = group.price

        # Internal Consultant
        if visit.internal_consultant:
            rule = CommissionRule.objects.filter(
                consultant_type='internal',
                consultant_id=visit.internal_consultant.id,
                test_group=group
            ).first()
            if rule:
                commissions.append({
                    'type': 'internal',
                    'name': visit.internal_consultant.name,
                    'group': group.name,
                    'amount': rule.calculate(price)
                })

        # External Consultant
        if visit.external_consultant:
            rule = CommissionRule.objects.filter(
                consultant_type='external',
                consultant_id=visit.external_consultant.id,
                test_group=group
            ).first()
            if rule:
                commissions.append({
                    'type': 'external',
                    'name': visit.external_consultant.name,
                    'group': group.name,
                    'amount': rule.calculate(price)
                })

        # Referrer
        if visit.referrer:
            rule = CommissionRule.objects.filter(
                consultant_type='referrer',
                consultant_id=visit.referrer.id,
                test_group=group
            ).first()
            if rule:
                commissions.append({
                    'type': 'referrer',
                    'name': visit.referrer.name,
                    'group': group.name,
                    'amount': rule.calculate(price)
                })

    return commissions
