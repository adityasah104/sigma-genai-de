#!/bin/bash
while true; do
  GIT_EDITOR=true git rebase --continue
  if [ $? -eq 0 ]; then
    echo "Rebase finished successfully!"
    break
  fi
  
  # Check if we are still rebasing
  if ! git status | grep -q "interactive rebase in progress"; then
    echo "Not rebasing anymore or unknown error."
    break
  fi
  
  # Get conflicted files
  conflicted=$(git diff --name-only --diff-filter=U)
  if [ -z "$conflicted" ]; then
    echo "No conflicted files found, maybe nothing to commit?"
    GIT_EDITOR=true git rebase --skip
    continue
  fi
  
  echo "Resolving conflicts..."
  for file in $conflicted; do
    if [[ "$file" == "api/submissions.py" || "$file" == "setup/check_submissions.py" || "$file" == "dashboard/index.html" || "$file" == "students.csv" ]]; then
      git checkout --ours "$file"
    else
      git checkout --theirs "$file"
    fi
    git add "$file"
  done
done
