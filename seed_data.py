"""
Database Seeder for Online Examination System
==============================================
Populates the database with:
- 1 Admin Faculty Account
- 5 Demo Enrolled Students across CS, IT, AI/DS
- 7 Core Academic Subjects
- 70+ Verified Multiple Choice Questions with Explanations & Difficulty Tags
- Published Examinations with duration, passing marks, and negative marking
- Sample Student Attempts with Verified Certificates
"""

import sys
import io
from datetime import datetime, timedelta

# Ensure UTF-8 stdout on Windows terminals
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app import create_app
from models import db, User, Subject, Question, Exam, Attempt, Answer


def seed_database(force=False):
    app = create_app()
    with app.app_context():
        print("[*] Initializing database tables...")
        if force or "--force" in sys.argv or "--reset" in sys.argv:
            print("[*] Resetting database tables for fresh sequential seed...")
            db.drop_all()
        db.create_all()

        # Check if database is already populated
        if not force and "--force" not in sys.argv and "--reset" not in sys.argv and User.query.first():
            print("⚡ Database already contains records. Skipping seed.")
            return

        print("[*] Creating Super Admin (Dean) & 9 Department HOD Admins...")
        # 1. Super Admin Account (Principal & Dean of Academics)
        super_admin = User(
            name="Dr. Sharon Samuel",
            roll_no="SUPERADMIN01",
            department="All Departments",
            email="sharon@oes.com",
            phone="+91 98000 11223",
            role="superadmin",
            is_active=True
        )
        super_admin.set_password("Sharon123")
        db.session.add(super_admin)

        # 2. 9 Department HOD Faculty Admins
        faculty_admins_data = [
            ("Prof. Bhushan Chaudhari", "FAC_IT01", "Information Technology", "bhushan@oes.com", "+91 98765 43210", "Bhushan123"),
            ("Dr. Rajesh Sharma", "FAC_CSE01", "Computer Science & Engineering", "hod.cse@oes.com", "+91 98765 43211", "Sharma123"),
            ("Dr. Amit Kulkarni", "FAC_AI01", "Artificial Intelligence & Data Science", "hod.aids@oes.com", "+91 98765 43212", "Kulkarni123"),
            ("Prof. Vikram Malhotra", "FAC_CY01", "Cyber Security & Digital Forensics", "hod.cyber@oes.com", "+91 98765 43213", "Vikram123"),
            ("Dr. Neha Deshmukh", "FAC_EC01", "Electronics & Communication Engineering", "hod.ece@oes.com", "+91 98765 43214", "Neha123"),
            ("Prof. Suresh Patil", "FAC_EE01", "Electrical Engineering", "hod.ee@oes.com", "+91 98765 43215", "Suresh123"),
            ("Dr. Sanjay Joshi", "FAC_ME01", "Mechanical Engineering", "hod.me@oes.com", "+91 98765 43216", "Sanjay123"),
            ("Prof. Ritu Saxena", "FAC_CE01", "Civil Engineering", "hod.ce@oes.com", "+91 98765 43217", "Ritu123"),
            ("Dr. Ananya Roy", "FAC_BT01", "Biotechnology Engineering", "hod.bt@oes.com", "+91 98765 43218", "Ananya123"),
        ]

        for fname, froll, fdept, femail, fphone, fpwd in faculty_admins_data:
            fac = User(
                name=fname,
                roll_no=froll,
                department=fdept,
                email=femail,
                phone=fphone,
                role="admin",
                is_active=True
            )
            fac.set_password(fpwd)
            db.session.add(fac)

        # 3. Default Registered Student (Sumit Kushwaha)
        students_data = [
            ("Sumit Kushwaha", "BCS2026001", "Computer Science & Engineering", "sumit@oes.com", "+91 98111 22334", "Sumit123"),
        ]

        if "--with-demo-students" in sys.argv:
            students_data.extend([
                ("Laukik Lakhat", "BIT2026001", "Information Technology", "lovekik@oes.com", "+91 98222 33445", "Laukik123"),
                ("Priya Verma", "BAI2026001", "Artificial Intelligence & Data Science", "priya@oes.com", "+91 98333 44556", "Priya123"),
                ("Rohit Sharma", "BCY2026001", "Cyber Security & Digital Forensics", "rohit@oes.com", "+91 98444 55667", "Rohit123"),
                ("Sneha Patel", "BEC2026001", "Electronics & Communication Engineering", "sneha@oes.com", "+91 98555 66778", "Sneha123"),
                ("Aman Singh", "BEE2026001", "Electrical Engineering", "aman@oes.com", "+91 98666 77889", "Aman123"),
                ("Vikas Yadav", "BME2026001", "Mechanical Engineering", "vikas@oes.com", "+91 98777 88990", "Vikas123"),
                ("Pooja Nair", "BCE2026001", "Civil Engineering", "pooja@oes.com", "+91 98888 99001", "Pooja123"),
                ("Rohan Roy", "BBT2026001", "Biotechnology Engineering", "rohan@oes.com", "+91 98999 00112", "Rohan123"),
                ("Sahil Gupta", "BCS2026002", "Computer Science & Engineering", "sahil@oes.com", "+91 98123 45678", "Sahil123"),
            ])

        created_students = []
        for name, roll, dept, email, phone, pwd in students_data:
            s = User(
                name=name,
                roll_no=roll,
                department=dept,
                email=email,
                phone=phone,
                role="student",
                is_active=True
            )
            s.set_password(pwd)
            db.session.add(s)
            created_students.append(s)

        db.session.commit()

        # 3. Create Academic Subjects for all 9 Departments + Aptitude
        print("[*] Populating Academic Subjects for all 9 Departments...")
        subjects_map = {}
        subject_info = [
            ("Python Programming", "PYTHON", "Python syntax, OOPs, data structures, list comprehensions, exceptions and modules.", "🐍", "Computer Science & Engineering"),
            ("Database Management Systems", "DBMS", "Relational database concepts, SQL queries, normalization, ACID properties, and indexing.", "🗄️", "Computer Science & Engineering"),
            ("Data Structures & Algorithms", "DSA", "Arrays, linked lists, stacks, queues, trees, sorting algorithms, and asymptotic complexity.", "🌳", "Computer Science & Engineering"),
            ("Operating Systems", "OS", "Process scheduling, CPU concurrency, deadlocks, virtual memory, paging, and system calls.", "💻", "Computer Science & Engineering"),
            ("Computer Networks", "CN", "OSI 7 Layers, TCP/IP protocol suite, HTTP/HTTPS, DNS, IP addressing, and subnetting.", "🌐", "Information Technology"),
            ("Web Development", "WEB", "Modern HTML5, CSS3 layout, JavaScript ES6+, REST APIs, and client-server architecture.", "⚡", "Information Technology"),
            ("Machine Learning & AI", "AIDS", "Supervised learning, deep neural networks, model optimization, and Python data pipelines.", "🧠", "Artificial Intelligence & Data Science"),
            ("Cyber Security & Forensics", "CYBER", "Network defense, penetration testing, cryptography, and digital threat intelligence.", "🛡️", "Cyber Security & Digital Forensics"),
            ("Embedded Systems & IoT", "ECE", "Microcontrollers, ARM architectures, sensor interfacing, and wireless protocols.", "📡", "Electronics & Communication Engineering"),
            ("Power Systems & Smart Grids", "EE", "Circuit analysis, transmission systems, transformer protection, and renewable energy.", "⚡", "Electrical Engineering"),
            ("Thermodynamics & CAD/CAM", "ME", "Kinematics, fluid dynamics, stress analysis, and automated CNC manufacturing.", "⚙️", "Mechanical Engineering"),
            ("Structural Engineering", "CE", "Beam mechanics, concrete technology, geotechnical surveying, and infrastructure design.", "🏗️", "Civil Engineering"),
            ("Bioinformatics & Genetics", "BT", "DNA sequencing, molecular genetics, protein folding, and cellular bioprocesses.", "🧬", "Biotechnology Engineering"),
            ("General Aptitude & Reasoning", "APT", "Quantitative reasoning, number series, logical deduction, and analytical problems.", "🧩", "All Departments"),
        ]

        for name, code, desc, icon, dept in subject_info:
            sub = Subject(name=name, code=code, department=dept, description=desc, icon=icon)
            db.session.add(sub)
            db.session.flush()
            subjects_map[code] = sub

        # 4. Question Bank (100+ MCQs across all 9 departments + Aptitude)
        print("[*] Seeding Questions with verified answers across all 9 departments...")
        questions_dataset = [
            # ---------------- PYTHON (10 MCQs) ----------------
            ("PYTHON", "Which of the following data types is immutable in Python?", "List", "Dictionary", "Tuple", "Set", "C", "Easy", "Tuples and strings are immutable in Python, meaning their elements cannot be changed after creation.", 2.5),
            ("PYTHON", "What will be the output of `type(lambda x: x*2)` in Python 3?", "<class 'function'>", "<class 'lambda'>", "<class 'int'>", "<class 'generator'>", "A", "Medium", "Lambda expressions in Python create standard anonymous function objects of type 'function'.", 2.5),
            ("PYTHON", "What is the purpose of the `__init__` method in Python classes?", "Destructor method", "Constructor for initializing instance attributes", "To import external modules", "To declare private variables", "B", "Easy", "`__init__` is the constructor method automatically executed when a new object instance is created.", 2.5),
            ("PYTHON", "Which keyword is used to handle exceptions that must always execute whether an error occurred or not?", "catch", "finally", "always", "except", "B", "Easy", "The `finally` block in Python always executes regardless of whether an exception was raised or handled.", 2.5),
            ("PYTHON", "What does the list comprehension `[x**2 for x in range(5) if x % 2 == 0]` evaluate to?", "[0, 4, 16]", "[1, 9]", "[0, 1, 4, 9, 16]", "[4, 16]", "A", "Medium", "Even numbers in range(5) are 0, 2, 4. Their squares are 0, 4, and 16.", 2.5),
            ("PYTHON", "What is the output of `print(0.1 + 0.2 == 0.3)` in Python?", "True", "False", "SyntaxError", "None", "B", "Medium", "Due to floating-point binary representation limits, 0.1 + 0.2 evaluates to 0.30000000000000004, so equality returns False.", 2.5),
            ("PYTHON", "How does Python handle memory management internally?", "Manual deallocation by programmer", "Automatic Reference Counting and Generational Garbage Collection", "Pointers only", "Stack memory exclusively", "B", "Hard", "Python uses reference counting as its primary mechanism alongside a cycle-detecting generational garbage collector.", 2.5),
            ("PYTHON", "Which module in Python is used to perform regular expression matching?", "regex", "re", "pyregex", "match", "B", "Easy", "The built-in `re` module provides full Perl-like regular expression matching operations.", 2.5),
            ("PYTHON", "What is the result of `bool([])` and `bool([0])`?", "False, False", "True, True", "False, True", "True, False", "C", "Easy", "Empty lists evaluate to False in boolean contexts, while non-empty collections like `[0]` evaluate to True.", 2.5),
            ("PYTHON", "What does the `*args` and `**kwargs` syntax in a function definition allow?", "Keyword arguments only", "Variable number of positional and keyword arguments", "Pointer dereferencing", "Data type annotations", "B", "Medium", "`*args` passes a variable number of non-keyword positional arguments, while `**kwargs` passes keyword arguments as a dictionary.", 2.5),

            # ---------------- DBMS (10 MCQs) ----------------
            ("DBMS", "In SQL, which clause is used to filter records resulting from a GROUP BY clause?", "WHERE", "HAVING", "FILTER", "ORDER BY", "B", "Easy", "HAVING filters groups created by GROUP BY, while WHERE filters individual rows before grouping.", 2.5),
            ("DBMS", "Which of the following is NOT an ACID property in relational databases?", "Atomicity", "Consistency", "Integrity", "Durability", "C", "Easy", "ACID stands for Atomicity, Consistency, Isolation, and Durability.", 2.5),
            ("DBMS", "A relation is in 2NF if and only if it is in 1NF and what other condition is satisfied?", "No multi-valued attributes", "No partial functional dependencies on candidate keys", "No transitive dependencies", "All attributes are atomic", "B", "Medium", "2NF eliminates partial dependency, meaning every non-prime attribute must depend on the whole candidate key.", 2.5),
            ("DBMS", "What type of JOIN returns all records when there is a match in either left or right table?", "INNER JOIN", "CROSS JOIN", "FULL OUTER JOIN", "LEFT JOIN", "C", "Easy", "FULL OUTER JOIN combines the results of both LEFT and RIGHT outer joins, returning matching and non-matching rows.", 2.5),
            ("DBMS", "Which command is used to remove all rows from a table quickly and deallocate data pages without logging individual row deletions?", "DELETE", "DROP", "TRUNCATE", "REMOVE", "C", "Medium", "TRUNCATE TABLE is a DDL command that deallocates data pages faster than row-by-row DELETE.", 2.5),
            ("DBMS", "What does BCNF stand for, and what is its primary requirement?", "Binary Common Normal Form", "Boyce-Codd Normal Form: for every X -> Y, X must be a super key", "Basic Component Normal Form", "Buffered Column Normal Form", "B", "Medium", "BCNF is a stricter version of 3NF where every determinant (X in X -> Y) must be a superkey.", 2.5),
            ("DBMS", "What is a Foreign Key in a relational schema?", "A key generated by external servers", "An attribute in one table that references the primary key of another table", "A secondary index", "A composite unique key", "B", "Easy", "A foreign key maintains referential integrity by referencing the primary key of another relation.", 2.5),
            ("DBMS", "Which isolation level prevents Dirty Reads but still allows Non-Repeatable Reads?", "Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable", "B", "Hard", "Read Committed prevents reading uncommitted data (dirty reads), but allows another transaction to modify rows between reads.", 2.5),
            ("DBMS", "Which index structure is most widely used by relational database engines for range queries?", "Hash Index", "B+ Tree Index", "Binary Search Tree", "Linked List Index", "B", "Medium", "B+ Trees store all data pointers at leaf nodes and link them sequentially, making range queries very efficient.", 2.5),
            ("DBMS", "Which SQL constraint ensures that all values in a column are distinct and not null?", "UNIQUE", "CHECK", "PRIMARY KEY", "FOREIGN KEY", "C", "Easy", "A PRIMARY KEY uniquely identifies each record and strictly disallows NULL values.", 2.5),

            # ---------------- DSA (10 MCQs) ----------------
            ("DSA", "What is the worst-case time complexity of QuickSort?", "O(n log n)", "O(n^2)", "O(n)", "O(log n)", "B", "Medium", "QuickSort degrades to O(n^2) when the pivot is consistently the smallest or largest element (e.g. already sorted array with naive pivot).", 2.5),
            ("DSA", "Which data structure operates strictly on a Last-In, First-Out (LIFO) basis?", "Queue", "Stack", "Priority Queue", "Deque", "B", "Easy", "A Stack operates on the LIFO principle where push and pop occur at the same top element.", 2.5),
            ("DSA", "What is the average time complexity to search for an element in a Balanced Binary Search Tree (AVL / Red-Black)?", "O(1)", "O(log n)", "O(n)", "O(n log n)", "B", "Easy", "In a balanced BST, tree height is log2(n), making search, insert, and delete operations O(log n).", 2.5),
            ("DSA", "Which algorithm is used to find the shortest path from a single source vertex to all other vertices in a graph with non-negative edge weights?", "Kruskal's Algorithm", "Dijkstra's Algorithm", "Prim's Algorithm", "Floyd-Warshall Algorithm", "B", "Medium", "Dijkstra's greedy algorithm finds the single-source shortest path in graphs with non-negative edge weights.", 2.5),
            ("DSA", "What is the space complexity of Depth First Search (DFS) on a graph with V vertices and maximum depth d?", "O(V^2)", "O(d)", "O(1)", "O(V * E)", "B", "Medium", "DFS uses a call stack proportional to the maximum recursion depth, which is O(d).", 2.5),
            ("DSA", "In a Max-Heap with n elements, what is the time complexity of deleting the maximum element (root)?", "O(1)", "O(log n)", "O(n)", "O(n log n)", "B", "Medium", "Deleting the root requires swapping with the last element and running heapify down, taking O(log n) time.", 2.5),
            ("DSA", "Which sorting algorithm is guaranteed to be stable and have O(n log n) worst-case time complexity?", "Merge Sort", "Quick Sort", "Heap Sort", "Selection Sort", "A", "Medium", "Merge Sort divides the array in half, merges in O(n) preserving relative order of equal elements, giving stable O(n log n).", 2.5),
            ("DSA", "What is the main advantage of a Doubly Linked List over a Singly Linked List?", "Uses less memory", "Can be traversed in both forward and backward directions", "Faster cache locality", "Always constant size", "B", "Easy", "Each node in a doubly linked list holds pointers to both next and previous nodes, enabling bidirectional traversal.", 2.5),
            ("DSA", "What is the optimal data structure to implement a Breadth First Search (BFS) traversal?", "Stack", "Queue", "Priority Queue", "Hash Map", "B", "Easy", "BFS visits neighbors level by level using a FIFO Queue.", 2.5),
            ("DSA", "What is the load factor of a hash table with 70 elements stored in 100 buckets?", "7.0", "0.7", "700", "0.07", "B", "Easy", "Load factor = (Number of stored items) / (Number of buckets) = 70 / 100 = 0.7.", 2.5),

            # ---------------- OPERATING SYSTEMS (10 MCQs) ----------------
            ("OS", "Which CPU scheduling algorithm is non-preemptive and assigns the CPU to the process that requests it first?", "Round Robin (RR)", "First-Come, First-Served (FCFS)", "Shortest Remaining Time First (SRTF)", "Priority Preemptive", "B", "Easy", "FCFS assigns the CPU in the order processes arrive without preemption.", 2.5),
            ("OS", "Which of the following is NOT one of Coffman's four conditions for a Deadlock to occur?", "Mutual Exclusion", "Hold and Wait", "Preemption allowed", "Circular Wait", "C", "Medium", "No Preemption is required for deadlock; allowing preemption eliminates deadlock.", 2.5),
            ("OS", "What is Thrashing in virtual memory management?", "Excessive time spent in page swapping rather than executing instructions", "Overclocking the CPU", "Memory fragmentation caused by malloc", "Deleting system files", "A", "Medium", "Thrashing happens when the working set of pages cannot fit in physical RAM, causing continuous page faults.", 2.5),
            ("OS", "What is the primary difference between a Process and a Thread?", "Processes share memory; threads have separate address spaces", "Threads within the same process share code, data, and open files, but have separate stacks and registers", "Processes are scheduled by GPU; threads by CPU", "Threads are hardware units", "B", "Medium", "A thread is a lightweight execution unit within a process sharing the same address space.", 2.5),
            ("OS", "What is the purpose of the Translation Lookaside Buffer (TLB)?", "Buffer disk I/O requests", "A hardware cache to speed up virtual-to-physical address translation", "Prevent CPU overheating", "Manage USB ports", "B", "Hard", "The TLB caches recent virtual-to-physical page table translations in high-speed hardware.", 2.5),
            ("OS", "Which system call in UNIX/Linux creates a new child process by duplicating the calling process?", "exec()", "fork()", "clone()", "spawn()", "B", "Easy", "`fork()` creates a new process by duplicating the parent process address space.", 2.5),
            ("OS", "What is Belady's Anomaly in operating systems?", "More page frames result in more page faults in FIFO page replacement", "CPU usage drops to zero", "Deadlock occurs with 1 process", "RAM gets corrupted", "A", "Hard", "Belady's Anomaly is the counter-intuitive phenomenon where increasing physical page frames increases page faults under FIFO.", 2.5),
            ("OS", "What synchronization tool was proposed by Edsger Dijkstra to solve the Critical Section Problem?", "Semaphores", "Mutex Locks", "Monitors", "Spinlocks", "A", "Easy", "Dijkstra introduced integer-based Semaphores with `wait()` (P) and `signal()` (V) atomic primitives.", 2.5),
            ("OS", "What is Internal Fragmentation in memory management?", "Unused memory between allocated partitions", "Unused memory inside an allocated fixed-size block/page", "Hard drive disk bad sectors", "Cache misses", "B", "Medium", "Internal fragmentation occurs when memory allocated to a process is slightly larger than the requested size.", 2.5),
            ("OS", "What is the main role of the Dispatcher module in the CPU scheduler?", "Select which process to run next from ready queue", "Give control of the CPU to the selected process (context switch & mode switch)", "Terminate zombie processes", "Compile C programs", "B", "Medium", "The scheduler selects the process; the dispatcher performs the context switch to actually load it onto the CPU.", 2.5),

            # ---------------- COMPUTER NETWORKS (10 MCQs) ----------------
            ("CN", "Which layer of the OSI model is responsible for end-to-end communication, flow control, and error recovery?", "Network Layer", "Transport Layer", "Data Link Layer", "Session Layer", "B", "Easy", "The Transport Layer (Layer 4, e.g. TCP and UDP) provides transparent transfer of data between end hosts.", 2.5),
            ("CN", "What is the default port number used by HTTPS for secure web traffic?", "80", "443", "8080", "22", "B", "Easy", "HTTP uses port 80, while secure HTTPS uses port 443 with TLS encryption.", 2.5),
            ("CN", "Which protocol dynamically assigns IP addresses to client devices joining a local area network?", "DNS", "DHCP", "ARP", "ICMP", "B", "Easy", "DHCP (Dynamic Host Configuration Protocol) automatically provides IP addresses, subnet masks, and gateways.", 2.5),
            ("CN", "What is the size of an IPv6 address compared to an IPv4 address?", "32 bits vs 128 bits", "128 bits vs 32 bits", "64 bits vs 128 bits", "256 bits vs 64 bits", "B", "Easy", "IPv4 addresses are 32 bits (4 bytes), whereas IPv6 addresses are 128 bits (16 bytes).", 2.5),
            ("CN", "What is the purpose of the Address Resolution Protocol (ARP)?", "Resolve Domain Names to IP addresses", "Resolve IPv4 addresses to physical MAC hardware addresses", "Route packets between autonomous systems", "Encrypt network packets", "B", "Medium", "ARP maps a known Layer 3 IP address to its corresponding Layer 2 Ethernet MAC address on a local segment.", 2.5),
            ("CN", "In TCP 3-Way Handshake connection establishment, what is the sequence of control packets exchanged?", "ACK -> SYN -> SYN-ACK", "SYN -> SYN-ACK -> ACK", "FIN -> ACK -> FIN-ACK", "RST -> SYN -> ACK", "B", "Medium", "The client sends SYN, the server responds with SYN-ACK, and the client finishes with ACK.", 2.5),
            ("CN", "Which protocol is used by the `ping` utility to test host reachability?", "TCP", "ICMP", "UDP", "SNMP", "B", "Easy", "The `ping` command sends ICMP Echo Request packets and waits for ICMP Echo Reply messages.", 2.5),
            ("CN", "What is the usable host capacity of a `/24` IPv4 subnet mask (255.255.255.0)?", "256 hosts", "254 hosts", "128 hosts", "512 hosts", "B", "Medium", "A /24 subnet has 2^8 = 256 total addresses minus 2 reserved (network address and broadcast address) = 254 usable hosts.", 2.5),
            ("CN", "Which routing algorithm is based on Dijkstra's Shortest Path algorithm and used in OSPF?", "Distance Vector Routing", "Link State Routing", "Path Vector Routing", "Flooding", "B", "Hard", "OSPF uses Link State Routing where every router knows the full graph topology and computes paths via Dijkstra.", 2.5),
            ("CN", "What does DNS stand for and what is its primary function?", "Domain Name System: translates human-readable hostnames to IP addresses", "Data Network Service: manages broadband speeds", "Digital Network Server: stores HTML files", "Direct Node Socket: establishes peer connections", "A", "Easy", "DNS acts as the internet's phonebook by translating domain names (e.g. google.com) to numeric IP addresses.", 2.5),

            # ---------------- WEB DEVELOPMENT (10 MCQs) ----------------
            ("WEB", "Which HTTP status code represents a successful request with content returned?", "200 OK", "201 Created", "304 Not Modified", "404 Not Found", "A", "Easy", "HTTP 200 OK indicates that the client request has succeeded and the payload is returned.", 2.5),
            ("WEB", "What is the primary difference between `let` and `var` in JavaScript (ES6+)?", "`let` is block-scoped, while `var` is function-scoped and hoisted", "`var` cannot be reassigned", "`let` is global only", "There is no difference", "A", "Medium", "`let` introduces block scoping (inside if/loops) and avoids unwanted hoisting bugs associated with `var`.", 2.5),
            ("WEB", "Which HTTP method is designed by RESTful convention to update a specific resource partially?", "PUT", "PATCH", "POST", "GET", "B", "Medium", "PATCH applies partial modifications to a resource, whereas PUT replaces the entire entity.", 2.5),
            ("WEB", "What is the purpose of the `SameSite` attribute on HTTP cookies?", "Set cookie expiration date", "Mitigate Cross-Site Request Forgery (CSRF) attacks", "Compress cookie payloads", "Enable cross-domain tracking", "B", "Hard", "`SameSite=Strict/Lax` prevents the browser from sending cookies along with cross-site requests, protecting against CSRF.", 2.5),
            ("WEB", "In CSS Flexbox, which property aligns flex items along the cross axis (vertically in row layout)?", "justify-content", "align-items", "flex-direction", "align-content", "B", "Easy", "`align-items` controls alignment along the cross axis, while `justify-content` controls the main axis.", 2.5),
            ("WEB", "What is the JavaScript Event Loop responsible for?", "Compiling code to machine bytecode", "Executing asynchronous callbacks from the task queue when the call stack is empty", "Handling DOM styling", "Managing SQL connections", "B", "Hard", "The event loop continuously monitors the Call Stack and moves callbacks from the Task/Microtask Queue to the stack.", 2.5),
            ("WEB", "Which HTML5 semantic element is most appropriate for containing the main navigation links of a website?", "<nav>", "<section>", "<aside>", "<header>", "A", "Easy", "The `<nav>` element represents a section of a page whose purpose is to provide navigation links.", 2.5),
            ("WEB", "What is a Promise in JavaScript?", "A guarantee that an API will not fail", "An object representing the eventual completion or failure of an asynchronous operation", "A synchronized thread lock", "A browser cookie wrapper", "B", "Medium", "A Promise is an object representing pending, fulfilled, or rejected states of an asynchronous action.", 2.5),
            ("WEB", "Which header is used by browsers and servers to negotiate Cross-Origin Resource Sharing (CORS)?", "Access-Control-Allow-Origin", "Content-Security-Policy", "X-Frame-Options", "Authorization", "A", "Medium", "`Access-Control-Allow-Origin` indicates whether the response can be shared with requesting origin.", 2.5),
            ("WEB", "What does the `async/await` syntax in JavaScript provide?", "Multithreaded CPU parallel execution", "Syntactic sugar on top of Promises for writing clean asynchronous code synchronously", "Local storage caching", "Memory garbage collection", "B", "Easy", "`async/await` allows writing asynchronous promise-based code in a clean, readable synchronous style.", 2.5),

            # ---------------- AI & DATA SCIENCE (5 MCQs) ----------------
            ("AIDS", "Which loss function is commonly used for binary classification in neural networks?", "Mean Squared Error", "Binary Cross-Entropy (Log Loss)", "Hinge Loss", "Huber Loss", "B", "Medium", "Binary Cross-Entropy measures the performance of a classification model whose output is a probability value between 0 and 1.", 2.5),
            ("AIDS", "What is Overfitting in machine learning models?", "Model performs poorly on training data", "Model memorizes training data but fails to generalize on unseen test data", "Dataset has missing values", "Model trains too fast", "B", "Easy", "Overfitting occurs when a model learns the noise in training data instead of generalizable patterns.", 2.5),
            ("AIDS", "Which algorithm is an ensemble method that builds multiple decision trees using bagging?", "K-Means", "Random Forest", "Support Vector Machines", "Linear Regression", "B", "Easy", "Random Forest builds multiple decision trees and merges their predictions together for higher accuracy.", 2.5),
            ("AIDS", "What does the ReLU activation function return for input x?", "max(0, x)", "1 / (1 + e^-x)", "tanh(x)", "x^2", "A", "Easy", "Rectified Linear Unit (ReLU) computes f(x) = max(0, x), setting negative values to zero.", 2.5),
            ("AIDS", "Which technique is used to reduce dimensionality of high-dimensional data while preserving variance?", "PCA (Principal Component Analysis)", "Backpropagation", "Gradient Descent", "Dropout", "A", "Medium", "PCA transforms features into orthogonal principal components maximizing variance.", 2.5),

            # ---------------- CYBER SECURITY (5 MCQs) ----------------
            ("CYBER", "Which type of cipher uses two different keys: a public key for encryption and a private key for decryption?", "Symmetric Cipher", "Asymmetric (Public-Key) Cipher", "Caesar Cipher", "Stream Cipher", "B", "Easy", "Asymmetric encryption (e.g. RSA, ECC) uses public/private key pairs.", 2.5),
            ("CYBER", "What is a SQL Injection (SQLi) vulnerability?", "Injecting malicious CSS into web forms", "Injecting rogue SQL commands into input fields to manipulate backend queries", "Flooding network ports with UDP packets", "Cracking passwords via brute force", "B", "Easy", "SQLi occurs when untrusted user input is directly concatenated into database query strings.", 2.5),
            ("CYBER", "Which security protocol encrypts communication between web browsers and servers?", "TLS / SSL", "FTP", "Telnet", "SNMP", "A", "Easy", "Transport Layer Security (TLS) ensures privacy and data integrity between web applications.", 2.5),
            ("CYBER", "What is the primary goal of a Distributed Denial of Service (DDoS) attack?", "Steal user passwords", "Overwhelm target servers with traffic from multiple sources to cause outage", "Encrypt hard drive files for ransom", "Sniff Wi-Fi packets", "B", "Medium", "DDoS floods server bandwidth and processing queues using distributed botnets.", 2.5),
            ("CYBER", "Which hashing algorithm generates a 256-bit cryptographic digest widely used in digital certificates?", "MD5", "SHA-256", "DES", "RC4", "B", "Easy", "SHA-256 is a member of the SHA-2 family producing a 256-bit fixed-length hash value.", 2.5),

            # ---------------- ELECTRONICS & COMM (5 MCQs) ----------------
            ("ECE", "Which protocol is a synchronous, full-duplex serial communication standard using MOSI, MISO, SCK, and SS lines?", "I2C", "SPI", "UART", "CAN", "B", "Medium", "Serial Peripheral Interface (SPI) is a 4-wire synchronous full-duplex bus.", 2.5),
            ("ECE", "What is the Nyquist Sampling Rate for a signal with maximum frequency component fm?", "fm", "2 * fm", "0.5 * fm", "4 * fm", "B", "Easy", "Nyquist theorem requires sampling at least at twice the maximum frequency (fs >= 2*fm) to prevent aliasing.", 2.5),
            ("ECE", "Which logic family offers the lowest power consumption in static states?", "TTL", "CMOS", "ECL", "RTL", "B", "Easy", "CMOS (Complementary Metal-Oxide-Semiconductor) consumes negligible static power.", 2.5),
            ("ECE", "What is the primary function of a Zener Diode in electronic circuits?", "Voltage Regulation / Reference", "RF Amplification", "Audio Modulation", "Current Rectification Only", "A", "Easy", "Zener diodes maintain a constant breakdown voltage across their terminals for regulation.", 2.5),
            ("ECE", "Which architecture is commonly used in modern ARM and RISC-V microcontrollers?", "CISC", "RISC", "VLIW", "SIMD Only", "B", "Easy", "ARM and RISC-V are based on Reduced Instruction Set Computer (RISC) architectures.", 2.5),

            # ---------------- ELECTRICAL ENGINEERING (5 MCQs) ----------------
            ("EE", "What is the relationship between frequency (f), poles (P), and synchronous speed (Ns) in an AC machine?", "Ns = (120 * f) / P", "Ns = (P * f) / 120", "Ns = 60 * f * P", "Ns = f / (2 * P)", "A", "Medium", "Synchronous speed in RPM is given by Ns = 120 * f / P.", 2.5),
            ("EE", "In a purely capacitive AC circuit, what is the phase relationship between current and voltage?", "Current leads voltage by 90 degrees", "Current lags voltage by 90 degrees", "Current and voltage are in phase", "Current leads voltage by 180 degrees", "A", "Easy", "In capacitors, current leads the applied voltage by 90 degrees (CIVIL mnemonic).", 2.5),
            ("EE", "Which transformer test is conducted to determine core/iron losses and magnetizing branch parameters?", "Short Circuit Test", "Open Circuit Test", "Sumpner's Test", "Load Test", "B", "Medium", "Open Circuit test is performed at rated voltage to measure core hysteresis and eddy current losses.", 2.5),
            ("EE", "What device is used to protect transmission lines from lightning surges?", "Buchholz Relay", "Lightning Arrester (Surge Diverter)", "Circuit Breaker", "Current Transformer", "B", "Easy", "Lightning arresters divert high-voltage transient surges harmlessly to ground.", 2.5),
            ("EE", "What is the ideal Power Factor for an industrial AC electrical network?", "0.0", "1.0 (Unity)", "0.5 Lagging", "Infinity", "B", "Easy", "Unity power factor (1.0) means apparent power equals real active power with zero reactive loss.", 2.5),

            # ---------------- MECHANICAL ENGINEERING (5 MCQs) ----------------
            ("ME", "Which thermodynamic cycle represents the ideal air-standard cycle for Spark Ignition (Petrol) engines?", "Diesel Cycle", "Otto Cycle", "Rankine Cycle", "Brayton Cycle", "B", "Easy", "The Otto Cycle consists of two isentropic and two constant-volume (isochoric) processes.", 2.5),
            ("ME", "What does Hooke's Law state within the proportional limit of elasticity?", "Stress is directly proportional to Strain", "Strain is proportional to Temperature", "Force equals Mass times Acceleration", "Shear stress is zero", "A", "Easy", "Hooke's Law states sigma = E * epsilon (Stress is proportional to Strain).", 2.5),
            ("ME", "Which fluid property is responsible for resistance to gradual deformation by shear or tensile stress?", "Density", "Viscosity", "Surface Tension", "Specific Gravity", "B", "Easy", "Viscosity represents internal fluid friction against relative motion.", 2.5),
            ("ME", "What is the primary function of a Flywheel in an internal combustion engine?", "Cool the engine cylinder", "Store rotational energy to smooth out torque fluctuations", "Pump lubricating oil", "Inject fuel into chamber", "B", "Medium", "Flywheels store kinetic energy during power strokes and deliver it during idle strokes.", 2.5),
            ("ME", "In CAD/CAM manufacturing, what does CNC stand for?", "Computerized Network Control", "Computer Numerical Control", "Centralized Node Computing", "Continuous Node Cutting", "B", "Easy", "CNC automates machine tool operations via pre-programmed computer numerical codes (G-code).", 2.5),

            # ---------------- CIVIL ENGINEERING (5 MCQs) ----------------
            ("CE", "What is the standard water-cement ratio for normal structural concrete mixes to achieve optimal strength?", "0.40 to 0.60", "0.10 to 0.20", "0.90 to 1.20", "1.50 to 2.00", "A", "Easy", "A water-cement ratio between 0.40 and 0.60 ensures adequate workability and high compressive strength.", 2.5),
            ("CE", "Which instrument is traditionally used in land surveying to measure both horizontal and vertical angles?", "Prismatic Compass", "Theodolite", "Dumpy Level", "Chain & Tape", "B", "Easy", "A Theodolite is a precision optical instrument for measuring angles in horizontal and vertical planes.", 2.5),
            ("CE", "In Structural Mechanics, what is the Bending Moment at a simple support at the end of a beam?", "Maximum", "Zero", "Infinity", "Equal to span length", "B", "Medium", "At a simple end support (hinged/roller), there is no rotational restraint, so bending moment is zero.", 2.5),
            ("CE", "Which test is used to measure the consistency and workability of fresh concrete on site?", "Slump Cone Test", "Tensile Split Test", "Core Cutter Test", "Standard Proctor Test", "A", "Easy", "The Slump Test measures concrete fluidity and workability before placement.", 2.5),
            ("CE", "What type of foundation is most suitable when topsoil has low bearing capacity and structural loads are heavy?", "Isolated Footing", "Raft / Mat Foundation or Piles", "Strip Foundation", "Pad Footing", "B", "Medium", "Raft/Mat or Deep Pile foundations distribute heavy building loads over deep competent strata.", 2.5),

            # ---------------- BIOTECHNOLOGY (5 MCQs) ----------------
            ("BT", "What enzyme is responsible for synthesizing cDNA molecules from an RNA template in molecular biology?", "DNA Polymerase I", "Reverse Transcriptase", "RNA Helicase", "DNA Ligase", "B", "Easy", "Reverse Transcriptase converts single-stranded RNA into complementary DNA (cDNA).", 2.5),
            ("BT", "Which laboratory technique is used to amplify specific segments of DNA exponentially across thermal cycles?", "ELISA", "PCR (Polymerase Chain Reaction)", "SDS-PAGE", "Western Blotting", "B", "Easy", "PCR uses primers and Taq polymerase to amplify target DNA millions of times.", 2.5),
            ("BT", "What is the primary function of Restriction Enzymes (Endonucleases) in recombinant DNA technology?", "Join DNA fragments together", "Cut double-stranded DNA at specific recognition palindromic sequences", "Synthesize RNA primers", "Degrade proteins", "B", "Medium", "Restriction enzymes act as molecular scissors cutting DNA at precise recognition sites.", 2.5),
            ("BT", "Which nucleotide base pairs with Adenine (A) in RNA molecules?", "Thymine (T)", "Uracil (U)", "Cytosine (C)", "Guanine (G)", "B", "Easy", "In RNA, Uracil (U) replaces Thymine (T) to pair with Adenine.", 2.5),
            ("BT", "What bioinformatics database hosted by NCBI is the primary repository for nucleotide sequence data?", "GenBank", "PDB (Protein Data Bank)", "UniProt", "KEGG", "A", "Easy", "GenBank is the comprehensive public database of nucleotide sequences produced by NCBI.", 2.5),

            # ---------------- APTITUDE & REASONING (10 MCQs) ----------------
            ("APT", "Find the next number in the sequence: 3, 7, 15, 31, 63, ...", "127", "125", "129", "94", "A", "Easy", "Pattern is (n * 2) + 1: (3*2+1=7), (7*2+1=15), (15*2+1=31), (31*2+1=63), (63*2+1=127).", 2.0),
            ("APT", "A train 240 meters long passes a pole in 24 seconds. How long will it take to pass a platform 650 meters long?", "89 seconds", "65 seconds", "100 seconds", "75 seconds", "A", "Medium", "Speed = 240/24 = 10 m/s. Total distance for platform = 240 + 650 = 890 m. Time = 890 / 10 = 89 seconds.", 2.0),
            ("APT", "If 'CODING' is coded as 'DPEJOH', how will 'PYTHON' be coded?", "QZUIPO", "QZUIOO", "QYTHOM", "RZVIPO", "A", "Easy", "Each letter is shifted forward by +1: P->Q, Y->Z, T->U, H->I, O->P, N->O.", 2.0),
            ("APT", "A person buys an article for ₹800 and sells it for ₹1000. What is the profit percentage?", "20%", "25%", "15%", "30%", "B", "Easy", "Profit = ₹1000 - ₹800 = ₹200. Profit % = (200 / 800) * 100 = 25%.", 2.0),
            ("APT", "If 6 men can complete a project in 10 days, how many days will 15 men take to complete the same work?", "4 days", "5 days", "3 days", "6 days", "A", "Easy", "Total Man-days = 6 * 10 = 60. Time for 15 men = 60 / 15 = 4 days.", 2.0),
            ("APT", "Pointing to a photograph, a man said: 'She is the daughter of my grandfather's only son.' How is she related to the man?", "Sister", "Mother", "Aunt", "Daughter", "A", "Medium", "Grandfather's only son is the man's father. The daughter of the man's father is his Sister.", 2.0),
            ("APT", "What is the compound interest on ₹10,000 at 10% per annum for 2 years compounded annually?", "₹2,100", "₹2,000", "₹1,200", "₹2,200", "A", "Medium", "Amount = 10000 * (1.1)^2 = 10000 * 1.21 = ₹12,100. CI = ₹12,100 - ₹10,000 = ₹2,100.", 2.0),
            ("APT", "Which number replaces the question mark: 2, 6, 12, 20, 30, 42, ?", "56", "54", "60", "48", "A", "Easy", "Differences are +4, +6, +8, +10, +12, +14. 42 + 14 = 56 (also n*(n+1): 7*8=56).", 2.0),
            ("APT", "Two numbers are in the ratio 3 : 5. If their sum is 160, what is the larger number?", "100", "60", "90", "110", "A", "Easy", "Let numbers be 3x and 5x. 8x = 160 -> x = 20. Larger number = 5 * 20 = 100.", 2.0),
            ("APT", "In a group of 50 students, 30 play Cricket, 25 play Football, and 10 play both. How many play neither?", "5", "10", "15", "0", "A", "Medium", "Total playing at least one = 30 + 25 - 10 = 45. Playing neither = 50 - 45 = 5 students.", 2.0),
        ]

        created_questions_by_subject = {}
        for sub_code, text, op_a, op_b, op_c, op_d, corr, diff, expl, marks in questions_dataset:
            sub = subjects_map.get(sub_code)
            if sub:
                q = Question(
                    subject_id=sub.id,
                    question_text=text,
                    option_a=op_a,
                    option_b=op_b,
                    option_c=op_c,
                    option_d=op_d,
                    correct_option=corr,
                    difficulty=diff,
                    explanation=expl,
                    marks=marks
                )
                db.session.add(q)
                db.session.flush()
                if sub_code not in created_questions_by_subject:
                    created_questions_by_subject[sub_code] = []
                created_questions_by_subject[sub_code].append(q)

        # 5. Create Ready-to-Test Published Examinations (Exactly 1 Flagship Exam per Department = 9 Exams Total)
        print("[*] Creating Exactly 9 Published Examinations (1 per Department)...")
        exams_meta = [
            # 1. Computer Science & Engineering (4 Subjects)
            (
                "Python Core & Advanced Certification Exam",
                "PYTHON",
                "Official university evaluation covering Python data structures, OOPs, list comprehensions, and exception handling.",
                30, 25.0, 12.5, 0.25, False, True, False, "Computer Science & Engineering"
            ),
            (
                "DBMS & SQL Query Mastery Exam",
                "DBMS",
                "Assessment on relational schema design, SQL DDL/DML, Normalization (1NF-BCNF), and ACID transaction properties.",
                25, 25.0, 12.5, 0.25, False, True, False, "Computer Science & Engineering"
            ),
            (
                "Data Structures & Algorithms Live Challenge",
                "DSA",
                "Algorithmic analysis of trees, sorting algorithms, graphs, Dijkstra, and complexity optimization.",
                35, 25.0, 12.5, 0.25, False, True, False, "Computer Science & Engineering"
            ),
            (
                "Operating Systems & Concurrency Mock Test",
                "OS",
                "Practice assessment for process synchronization, CPU scheduling, semaphores, and virtual memory thrashing.",
                20, 25.0, 10.0, 0.0, True, True, False, "Computer Science & Engineering"
            ),
            # 2. Information Technology (2 Subjects)
            (
                "Full-Stack Web Development Assessment",
                "WEB",
                "Covers modern HTML5, CSS Flexbox, JavaScript ES6+, RESTful APIs, and asynchronous promises.",
                30, 25.0, 12.5, 0.25, False, True, False, "Information Technology"
            ),
            (
                "Computer Networks & OSI Protocols Exam",
                "CN",
                "Examination covering OSI 7 layers, TCP/IP handshake, subnetting, DNS, ARP, and routing algorithms.",
                25, 25.0, 12.5, 0.25, False, True, False, "Information Technology"
            ),
            # 3. AI & Data Science
            (
                "Machine Learning & Neural Networks Exam",
                "AIDS",
                "Core evaluation covering loss functions, supervised classification, deep neural networks, and dimensionality reduction.",
                30, 25.0, 12.5, 0.25, False, True, False, "Artificial Intelligence & Data Science"
            ),
            # 4. Cyber Security & Forensics
            (
                "Ethical Hacking & Network Defense Exam",
                "CYBER",
                "Covers asymmetric encryption, SQLi prevention, TLS/SSL protocols, and DDoS mitigation strategies.",
                25, 25.0, 12.5, 0.25, False, True, False, "Cyber Security & Digital Forensics"
            ),
            # 5. Electronics & Communication
            (
                "Embedded Systems & IoT Protocols Exam",
                "ECE",
                "Assessment on SPI bus standards, Nyquist sampling theorem, CMOS logic, and ARM architectures.",
                25, 25.0, 12.5, 0.25, False, True, False, "Electronics & Communication Engineering"
            ),
            # 6. Electrical Engineering
            (
                "Power Systems & Smart Grids Exam",
                "EE",
                "Synchronous AC machine calculations, power factor correction, transformer open-circuit testing, and surge protection.",
                25, 25.0, 12.5, 0.25, False, True, False, "Electrical Engineering"
            ),
            # 7. Mechanical Engineering
            (
                "Thermodynamics & CAD/CAM Design Exam",
                "ME",
                "Evaluation on Otto thermodynamic cycles, Hooke's law elasticity, fluid viscosity, and CNC manufacturing.",
                25, 25.0, 12.5, 0.25, False, True, False, "Mechanical Engineering"
            ),
            # 8. Civil Engineering
            (
                "Structural Analysis & Surveying Exam",
                "CE",
                "Covers concrete water-cement ratios, theodolite surveying, bending moment mechanics, and slump testing.",
                25, 25.0, 12.5, 0.25, False, True, False, "Civil Engineering"
            ),
            # 9. Biotechnology Engineering
            (
                "Bioinformatics & Genetic Engineering Exam",
                "BT",
                "Molecular biology evaluation covering reverse transcriptase, PCR thermal amplification, restriction enzymes, and GenBank.",
                25, 25.0, 12.5, 0.25, False, True, False, "Biotechnology Engineering"
            ),
            # 10. Universal (All Departments)
            (
                "General Aptitude & Logical Reasoning Test",
                "APT",
                "Quantitative problem solving, sequences, time-distance calculations, and analytical deductions.",
                20, 20.0, 10.0, 0.0, True, True, False, "All Departments"
            )
        ]

        created_exams = []
        for title, sub_code, desc, dur, tot_m, pass_m, neg_m, multi, shuf, webc, dept in exams_meta:
            sub = subjects_map.get(sub_code)
            exam = Exam(
                title=title,
                subject_id=sub.id,
                department=dept,
                description=desc,
                duration_minutes=dur,
                total_marks=tot_m,
                passing_marks=pass_m,
                negative_marks=neg_m,
                allow_multiple_attempts=multi,
                shuffle_questions=shuf,
                require_webcam=webc,
                is_published=True,
                created_by=super_admin.id
            )
            # Attach all subject questions
            exam.questions = created_questions_by_subject.get(sub_code, [])
            db.session.add(exam)
            db.session.flush()
            created_exams.append(exam)

        db.session.commit()

        # 6. Create realistic completed attempts and certificates for Demo Students
        print("[*] Generating Sample Verified Certificates and Attempts for Leaderboards...")
        # Sumit took Python Exam with distinction (Grade A+)
        python_exam = created_exams[0]
        sumit = created_students[0]
        att1 = Attempt(
            student_id=sumit.id,
            exam_id=python_exam.id,
            started_at=datetime.utcnow() - timedelta(hours=3, minutes=25),
            submitted_at=datetime.utcnow() - timedelta(hours=3),
            score=22.5,
            total_marks=25.0,
            percentage=90.0,
            grade="A+",
            is_passed=True,
            violations_count=0,
            status="completed"
        )
        att1.generate_certificate_id()
        db.session.add(att1)
        db.session.flush()

        # Answers for Sumit
        for q in python_exam.questions:
            ans = Answer(
                attempt_id=att1.id,
                question_id=q.id,
                selected_option=q.correct_option,
                is_correct=True,
                marks_awarded=q.marks
            )
            db.session.add(ans)

        # Sahil took IT Web Exam with Grade A (only if demo students created)
        if len(created_students) > 1:
            web_exam = created_exams[1]
            sahil = created_students[1]
            att2 = Attempt(
                student_id=sahil.id,
                exam_id=web_exam.id,
                started_at=datetime.utcnow() - timedelta(hours=5, minutes=20),
                submitted_at=datetime.utcnow() - timedelta(hours=5),
                score=20.0,
                total_marks=25.0,
                percentage=80.0,
                grade="A",
                is_passed=True,
                violations_count=1,
                status="completed"
            )
            att2.generate_certificate_id()
            db.session.add(att2)
            db.session.flush()

            for q in web_exam.questions:
                ans = Answer(
                    attempt_id=att2.id,
                    question_id=q.id,
                    selected_option=q.correct_option,
                    is_correct=True,
                    marks_awarded=q.marks
                )
                db.session.add(ans)

        # 7. Seed Official Announcements & Notifications (Optional)
        if "--with-demo-notifications" in sys.argv:
            print("[*] Seeding Official Announcements & Notifications...")
            from models import Notification
            notifs = [
                Notification(
                    title="📢 Mid-Term Examination Schedule & Guidelines Released",
                    message="All registered candidates are advised to verify their department and roll numbers. Live proctoring, countdown timers, and fullscreen anti-cheating mode are active on all official examinations.",
                    category="announcement",
                    priority="urgent",
                    sender_name="Prof. Bhushan Chaudhari",
                    target_role="student",
                    target_department=None,
                    is_read=False
                ),
            ]
            for n in notifs:
                db.session.add(n)

        db.session.commit()
        print("[+] Database successfully seeded!")


if __name__ == "__main__":
    seed_database()
