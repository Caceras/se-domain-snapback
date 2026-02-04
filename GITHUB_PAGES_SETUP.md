# GitHub Pages Setup Instructions

This repository is now configured for GitHub Pages deployment. Follow these steps to enable it:

## Enable GitHub Pages

1. Go to your repository on GitHub: https://github.com/Caceras/se-domain-snapback
2. Click on **Settings** (top right)
3. In the left sidebar, click on **Pages**
4. Under "Build and deployment":
   - Source: Select **GitHub Actions** (not "Deploy from a branch")
5. Click **Save**

That's it! GitHub Pages is now enabled.

## Verify Deployment

After enabling GitHub Pages:

1. Go to the **Actions** tab in your repository
2. You should see the "Deploy to GitHub Pages" workflow running
3. Wait for it to complete (usually takes 1-2 minutes)
4. Your site will be live at: **https://caceras.github.io/se-domain-snapback/**

## Automatic Updates

The site will automatically update:
- **Daily at 07:00 UTC** when the daily scan completes
- Whenever you manually trigger the "Daily Domain Scan" workflow
- Whenever you push to the main branch

## Manual Deployment

To manually trigger a deployment:

1. Go to the **Actions** tab
2. Select "Deploy to GitHub Pages" workflow
3. Click **Run workflow**
4. Select the branch (usually main or your current branch)
5. Click **Run workflow**

## Troubleshooting

If the site doesn't appear:

1. Check that GitHub Pages is enabled in Settings → Pages
2. Verify that "Source" is set to "GitHub Actions" (not branch)
3. Check the Actions tab for any failed workflow runs
4. Ensure the `docs/` directory contains `index.html` and report files

## Files Structure

```
docs/
├── index.html              # Main page with latest results
├── report-2026-02-05.html  # Individual report pages
├── report-2026-02-04.html
└── ...                     # One HTML file per scan date
```

## Customization

To customize the site appearance, edit `build_static_site.py` and modify:
- CSS styles in the `<style>` sections
- HTML structure in the generation functions
- Colors, fonts, or layout

After making changes, run `python build_static_site.py` locally to test, then commit and push.
