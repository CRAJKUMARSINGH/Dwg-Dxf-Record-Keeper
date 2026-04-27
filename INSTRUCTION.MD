# Next Steps: Git LFS Configuration for External Repositories

This guide provides the exact commands to replicate the Git LFS setup from `Bridge-Drawing-Manager` to your other project folders.

## 1. Setup for `Bridge_Slab_Design`

Run these commands in your PowerShell or Command Prompt:

1.  **Navigate to the project folder:**
    ```powershell
    cd C:\Users\Rajkumar\Bridge_Slab_Design
    ```
2.  **Initialize Git LFS:**
    ```powershell
    git lfs install
    ```
3.  **Apply Tracking Rules:**
    Copy the `.gitattributes` file from `Bridge-Drawing-Manager` to this folder:
    ```powershell
    copy C:\Users\Rajkumar\Bridge-Drawing-Manager\.gitattributes .gitattributes
    ```
4.  **Commit the configuration:**
    ```powershell
    git add .gitattributes
    git commit -m "chore: Initialize Git LFS and configure .gitattributes"
    ```

---

## 2. Setup for `Dwg-Dxf-Record-Keeper`

This repository is known to have a large history of binary files. Follow these steps to migrate them properly.

1.  **Navigate to the project folder:**
    ```powershell
    cd C:\Users\Rajkumar\Dwg-Dxf-Record-Keeper
    ```
2.  **Initialize Git LFS:**
    ```powershell
    git lfs install
    ```
3.  **Apply Tracking Rules:**
    ```powershell
    copy C:\Users\Rajkumar\Bridge-Drawing-Manager\.gitattributes .gitattributes
    ```
4.  **Migrate Existing History (Crucial):**
    To move existing `.dwg`, `.dxf`, and other binaries from git history into LFS (shrinking the repo size), run:
    ```powershell
    git lfs migrate import --everything --include="*.dwg,*.dxf,*.pdf,*.xlsx,*.docx,*.png,*.jpg,*.zip"
    ```
    *Note: This command will rewrite your git history. It is highly recommended to have a backup before running this.*

5.  **Finalize and Push:**
    ```powershell
    git add .gitattributes
    git commit -m "chore: Migrate large binaries to Git LFS"
    # If pushing to GitHub:
    git push --force
    ```

---

## 3. General Workflow Tips

*   **Adding new files:** Just add them normally with `git add`. If the extension matches `.gitattributes`, Git LFS handles it automatically.
*   **Verification:** Run `git lfs ls-files` to see which files are currently managed by LFS.
*   **Repo Size:** You should notice a significant decrease in `.git` folder size after a successful migration.
