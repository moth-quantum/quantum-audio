# Contributing Guidelines

Thank you for considering contributing to our project! To ensure compliance with our coding standards, please follow these guidelines:

## Steps for Contributing Code

1. **Fork the Repository**
   - Click the "Fork" button at the top right of this repository to create your own copy.

2. **Clone Your Fork**
   - Clone your forked repository to your local machine:
     ```bash
     git clone https://github.com/moth-quantum/quantum-audio.git
     ```

3. **Create a Branch**
   - Create a new branch for your changes:
     ```bash
     git checkout -b your-branch-name
     ```

4. **Make Your Changes**
   - Implement your feature or fix your bug.

5. **Write Tests**
   - **Add Tests:** Write tests for new features and bug fixes. Ensure that all new code is covered by tests. The tests folder is located [here](https://github.com/moth-quantum/quantum-audio/tree/main/tests).
   - **Testing Framework:** We use `pytest`. It can be installed on your python environment using:
     ```bash
      pip install pytest
      ```
   - **Run Tests:** Before submitting your pull request (PR), run the tests to verify that they pass:
     ```bash
     python -m pytest
     ```

7. **Document Your Changes**
   - **Docstrings:** Use Google-style docstrings to document your code. Follow the Google Python Style Guide for consistency:
     ```python
     def function_name(param1, param2):
         """
         Brief description of the function.

         Args:
             param1 (type): Description of param1.
             param2 (type): Description of param2.

         Returns:
             type: Description of return value.
         """
         pass
     ```
   - **Update Documentation:** Update the project’s documentation if your changes affect how the project is used. This may involve editing README files or other documentation files.

8. **Use Linting**
   - **Linting Tool:** We use `ruff` for linting. Ensure that your code adheres to our linting standards.
   - **Ruff Configuration:** Please check our `ruff` configuration [here](.ruff.toml).
   - **Run Linter:** Before submitting your PR, run `ruff` to check for any issues:
     ```bash
     ruff check .
     ```
   - **Fix Issues:** Address any linting issues reported by `ruff`.

9. **Commit Your Changes**
   - Write clear, concise commit messages. Follow the commit message guidelines provided in the project (e.g., conventional commits).
     ```bash
     git add .
     git commit -m "Describe your changes here"
     ```

10. **Push Your Branch**
   - Push your branch to your forked repository:
     ```bash
     git push origin your-branch-name
     ```

11. **Submit a Pull Request (PR)**
    - Open a pull request from your forked repository to the main repository.
    - Provide a clear description of your changes, including any relevant information such as related issues or the rationale behind your changes.
    - Ensure your PR adheres to the Apache 2.0 License and includes a clear description of the changes.

## Code of Conduct
Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) while contributing.

## Additional Notes
- **Communication:** If you have any questions or need clarification, feel free to reach out by opening an issue or contacting us via qap.support@mothquantum.com.
- **Review Process:** Your pull request will be reviewed by the maintainers. Feedback will be provided, and you may need to make additional changes based on that feedback.

Thank you for contributing to our project!
