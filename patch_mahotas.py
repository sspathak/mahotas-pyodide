import os
import re

def aggressive_patch():
    # This pattern looks for the return of a PyModule_Create call, 
    # which is the absolute last step of any Python extension init.
    pattern = re.compile(r'(return\s+PyModule_Create\s*\()', re.IGNORECASE)

    print("🛡️ Starting the Mahotas NumPy 2.0 Guard...")
    count = 0

    for root, dirs, files in os.walk('mahotas'):
        for file in files:
            if file.endswith('.cpp'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', errors='ignore') as f:
                    lines = f.readlines()

                content = "".join(lines)
                
                # If it already has it, or doesn't have the creation call, skip
                if 'import_array();' in content or 'PyModule_Create' not in content:
                    continue

                new_lines = []
                file_patched = False
                for line in lines:
                    if 'PyModule_Create' in line:
                        # We inject the initialization right before the module is returned to Python
                        print(f"✅ Patching Entry Point: {filepath}")
                        new_lines.append("    if (PyArray_API == NULL) { import_array(); }\n")
                        file_patched = True
                    new_lines.append(line)
                
                if file_patched:
                    with open(filepath, 'w') as f:
                        f.writelines(new_lines)
                    count += 1

    print(f"\n✨ Mission Success: {count} modules modernized.")

if __name__ == "__main__":
    aggressive_patch()