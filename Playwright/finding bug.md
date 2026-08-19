# Bug Findings Log

Dokumen ini digunakan untuk mencatat seluruh temuan bug pada automation atau exploratory testing eDOT. Setiap temuan baru diberi ID berurutan dan mengikuti template pada bagian **Reusable Bug Template**.

## Findings Index

| ID      | Title                                                  | Module             | Severity | Priority | Status |
| ------- | ------------------------------------------------------ | ------------------ | -------- | -------- | ------ |
| BUG-001 | Deleted company remains visible on the `Companies` tab | Company Management | Major    | High     | Open   |

## Reusable Bug Template

Salin bagian berikut untuk membuat temuan baru. Ganti ID dengan nomor berikutnya, lalu lengkapi field yang relevan.

```markdown
## BUG-XXX: [Short, actionable bug title]

### Issue Summary

| Field             | Detail                                         |
| ----------------- | ---------------------------------------------- |
| **Issue Type**    | Bug                                            |
| **Status**        | Open                                           |
| **Priority**      | High / Medium / Low                            |
| **Severity**      | Blocker / Critical / Major / Minor / Trivial   |
| **Module**        | [Feature or module]                            |
| **Component**     | [Page, flow, or component]                     |
| **Environment**   | [URL, browser, OS, build, or test environment] |
| **Reported Date** | [DD Month YYYY]                                |
| **Reporter**      | [Name or team]                                 |

### Description

[What is wrong and under what condition does it occur?]

### Preconditions

- [Required account, data, permission, or setup]

### Steps to Reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Result

- [Expected behavior]

### Actual Result

- [Observed behavior]

### Impact

- [User, business, data, or testing impact]

### Evidence

- [Screenshot, video, log, or report link]

### Suggested Investigation Areas

- [Relevant UI, API, state, data, or integration area]

### Acceptance Criteria

- [Condition that confirms the bug is fixed]

### Verification Notes

[Retest scope and regression checks after the fix.]
```

## BUG-001: Deleted Company Still Visible on Companies Tab

### Issue Summary

| Field             | Detail                                                 |
| ----------------- | ------------------------------------------------------ |
| **Issue Type**    | Bug                                                    |
| **Title**         | Deleted company remains visible on the `Companies` tab |
| **Status**        | Open                                                   |
| **Priority**      | High                                                   |
| **Severity**      | Major                                                  |
| **Module**        | Company Management                                     |
| **Component**     | Companies tab / Company deletion                       |
| **Environment**   | eDOT web application                                   |
| **Reported Date** | 19 August 2026                                         |

### Description

After a company is deleted, the deleted company is still displayed on the `Companies` tab. When the user clicks **Manage** on the displayed company, the company detail data is `null`.

This indicates that the company record may already be deleted from the source data, but the Companies list is not refreshed or is displaying stale data.

### Preconditions

- User is authenticated in the eDOT web application.
- At least one company exists in the **Companies** tab.
- User has permission to delete a company.

### Steps to Reproduce

1. Open the **Companies** tab.
2. Select an existing company.
3. Delete the company.
4. Return to or refresh the **Companies** tab.
5. Search for or locate the deleted company.
6. Click **Manage** on the deleted company.

### Expected Result

- The deleted company is removed from the **Companies** tab.
- The deleted company cannot be found through the company list or search.
- No **Manage** action is available for the deleted company.

### Actual Result

- The deleted company remains visible on the **Companies** tab.
- The user can still click **Manage**.
- The company detail data displayed after opening **Manage** is `null`.

### Impact

- Users may believe that the deletion did not succeed.
- The Companies list contains stale or invalid records.
- Users can access a company entry that has no valid detail data.
- This can reduce trust in company data and may lead to incorrect follow-up actions.

### Evidence

- Jam recording: [View video evidence](https://jam.dev/c/23b3b183-d28c-44eb-937f-9fd4101a8ea2)

### Suggested Investigation Areas

- Refresh or invalidate the Companies list after a successful delete response.
- Verify that deleted records are excluded from the Companies list API response.
- Check whether the list uses cached data that is not cleared after deletion.
- Verify that the UI handles a `null` company detail response by removing the stale entry or showing an appropriate not-found state.

### Acceptance Criteria

- A successfully deleted company no longer appears on the **Companies** tab without requiring a full browser restart.
- Refreshing the page does not restore the deleted company.
- The deleted company cannot be opened through **Manage**.
- If a stale entry is encountered, the UI displays a clear not-found state and removes or refreshes the invalid entry.
- Existing companies remain visible and their detail data is unaffected.

### Verification Notes

Retest the deletion flow after the fix using both:

- A company deleted from the Companies list.
- A page refresh after deletion.

Confirm that the deleted company is absent from the list and that no `null` detail page can be opened.
