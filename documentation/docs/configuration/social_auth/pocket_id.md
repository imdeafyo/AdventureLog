# Pocket ID OIDC Authentication

<img src="https://pocket-id.org/logo.png" alt="Pocket ID Logo" width="400" />

Pocket ID is a lightweight, self-hosted OpenID Connect (OIDC) identity provider. AdventureLog can be configured to use Pocket ID for social authentication using its built-in OpenID Connect support.

Once Pocket ID is configured by an administrator, users can sign in to AdventureLog using their Pocket ID account and optionally link it to an existing AdventureLog account.

---

# Configuration

To enable Pocket ID as an identity provider, both Pocket ID and AdventureLog must be configured correctly. The most important (and least obvious) part of this setup is the **callback URL**, which must match AdventureLog’s internal OIDC routing.

---

## Pocket ID Configuration

1. Log in to your Pocket ID admin interface.

2. Navigate to **Clients** and create a new client.

3. Name the client something like `AdventureLog`.

4. Set the **Redirect / Callback URL** to:

   ```
   https://<adventurelog-backend.example.com>/accounts/oidc/<CLIENT_ID>/login/callback/
   ```

   - Replace `<adventurelog-backend.example.com>` with the **backend** URL of your AdventureLog instance.
   - Replace `<CLIENT_ID>` with the **Pocket ID client ID** exactly as generated.
   - This path is required and currently not auto-documented by Pocket ID or AdventureLog.

5. Ensure the client type is **Confidential**.

6. Copy the generated **Client ID** and **Client Secret** — you will need both for AdventureLog.

---

## AdventureLog Configuration

This configuration is done in the [Admin Panel](../../guides/admin_panel.md). You can launch it from the `Settings` page or navigate directly to `/admin` on your AdventureLog server.

1. Log in to AdventureLog as an administrator.
2. Navigate to **Settings** → **Administration Settings** and launch the admin panel.
3. Go to **Social Accounts**.
4. Under **Social applications**, click **Add**.
5. Fill in the fields as follows:

### Social Application Settings

- **Provider**: `OpenID Connect`
- **Provider ID**: Pocket ID Client ID
- **Name**: `Pocket ID`
- **Client ID**: Pocket ID Client ID
- **Secret Key**: Pocket ID Client Secret
- **Key**: _(leave blank)_
- **Settings**:

```json
{
  "server_url": "https://<pocketid-url>/.well-known/openid-configuration"
}
```

- Replace `<pocketid-url>` with the base URL of your Pocket ID instance.

::: warning
Do **not** use `localhost` unless Pocket ID is running on the same machine and is resolvable from inside the AdventureLog container or service. Use a domain name or LAN IP instead.
:::

- **Sites**: Move the sites you want Pocket ID enabled on (usually `example.com` and `www.example.com`).

6. Save the configuration.

Ensure Pocket ID is running and reachable by AdventureLog.

---

## What It Should Look Like

Once configured correctly:

- Pocket ID appears as a login option on the AdventureLog login screen.
- Logging in redirects to Pocket ID, then back to AdventureLog without errors.

---

## Linking to an Existing Account

If a user already has an AdventureLog account:

1. Log in to AdventureLog normally.
2. Go to **Settings**.
3. Click **Launch Account Connections**.
4. Choose **Pocket ID** to link the identity to the existing account.

This allows future logins using Pocket ID without creating a duplicate account.

---

## Troubleshooting

### 404 Error After Login

Ensure that:

- `/accounts` routes are handled by the **backend**, not the frontend.
- Your reverse proxy (Nginx, Traefik, Caddy, etc.) forwards `/accounts/*` correctly.

---

### Invalid Redirect URI

- Double-check that the callback URL in Pocket ID exactly matches:

```
/accounts/oidc/<CLIENT_ID>/login/callback/
```

- The `<CLIENT_ID>` must match the value used in the AdventureLog social application.

---

### Cannot Reach Pocket ID

- Verify that the `.well-known/openid-configuration` endpoint is accessible from the AdventureLog server.
- Test by opening:

```
https://<pocketid-url>/.well-known/openid-configuration
```

in a browser.

---

## Notes

- Pocket ID configuration is very similar to Authentik.
- The main difference is the **explicit callback URL requirement** and the use of the `.well-known/openid-configuration` endpoint as the `server_url`.
- This setup works with Docker, Docker Compose, and bare-metal deployments as long as networking i
