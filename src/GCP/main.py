import functions_framework

@functions_framework.http
def print_country(request):
    country = request.args.get("country")
    if not country:
        body = request.get_json(silent=True, force=True) or {}
        country = body.get("country", "Unknown")
    print(f"Country: {country}")
    return f"Country: {country}"

# silent=True → won't throw an error if body isn't valid JSON
# force=True → parses JSON even if Content-Type header isn't application/json
# .get("country", "Unknown") → returns "Unknown" if country key is missing in JSON body