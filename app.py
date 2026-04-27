import streamlit as st
from datetime import datetime, date
from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, Recurrence

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — initialise once, persist across reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", email="")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner: Owner     = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    name_input = st.text_input("Name", value=owner.name or "Jordan")
with col2:
    email_input = st.text_input("Email", value=owner.email or "jordan@example.com")

if name_input:
    owner.name = name_input
if email_input:
    owner.email = email_input

# ---------------------------------------------------------------------------
# Section 2 — Add a Pet
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species  = st.selectbox("Species", ["dog", "cat", "bird", "other"])
with col3:
    breed    = st.text_input("Breed", value="Mixed")

col4, col5 = st.columns(2)
with col4:
    age    = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
with col5:
    weight = st.number_input("Weight (kg)", min_value=0.1, max_value=200.0, value=5.0)

if st.button("Add pet"):
    if pet_name in [p.name for p in owner.pets]:
        st.warning(f"'{pet_name}' is already registered.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, breed=breed,
                          age=int(age), weight=float(weight)))
        st.success(f"Added {pet_name} to {owner.name}'s profile.")

if owner.pets:
    st.markdown("**Registered pets:** " +
                ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet — add one above.")

# ---------------------------------------------------------------------------
# Section 3 — Add a Task
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    pet_names    = [p.name for p in owner.pets]
    selected_pet = st.selectbox("Assign to pet", pet_names, key="task_pet")

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        task_type  = st.selectbox("Type", [t.value for t in TaskType])
        priority   = st.number_input("Priority (1 = highest)", min_value=1, max_value=5, value=1)
    with col2:
        task_date  = st.date_input("Due date", value=date.today())
        task_time  = st.time_input("Due time",
                                   value=datetime.now().time().replace(second=0, microsecond=0))
        recurrence = st.selectbox("Recurrence", [r.value for r in Recurrence])
    notes = st.text_input("Notes (optional)", value="")

    if st.button("Add task"):
        pet_obj = next(p for p in owner.pets if p.name == selected_pet)
        new_task = Task(
            title        = task_title,
            task_type    = TaskType(task_type),
            due_datetime = datetime.combine(task_date, task_time),
            priority     = int(priority),
            recurrence   = Recurrence(recurrence),
            notes        = notes,
        )
        pet_obj.add_task(new_task)
        scheduler.load_from_owner(owner)   # keep scheduler in sync
        st.success(f"Task '{task_title}' added to {selected_pet}.")

    # Task list for the selected pet — sorted by time
    pet_obj   = next(p for p in owner.pets if p.name == selected_pet)
    pet_tasks = scheduler.sort_by_time(scheduler.get_tasks_for_pet(pet_obj))

    if pet_tasks:
        st.markdown(f"**{selected_pet}'s tasks ({len(pet_tasks)}):**")
        st.table([
            {
                "Time":       t.due_datetime.strftime("%Y-%m-%d %I:%M %p"),
                "Title":      t.title,
                "Type":       t.task_type.value,
                "Priority":   t.priority,
                "Recurrence": t.recurrence.value,
                "Done":       "Yes" if t.is_complete else "No",
                "Notes":      t.notes or "—",
            }
            for t in pet_tasks
        ])
    else:
        st.info(f"No tasks for {selected_pet} yet.")

# ---------------------------------------------------------------------------
# Section 4 — Mark a Task Complete (with auto-recurrence)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Mark Task Complete")

all_incomplete = [t for t in scheduler.tasks if not t.is_complete]
if not all_incomplete:
    st.info("No incomplete tasks in the scheduler yet.")
else:
    # Build label → task map for the selectbox
    def task_label(t: Task) -> str:
        pet_name = next(
            (p.name for p in owner.pets if any(x.id == t.id for x in p.tasks)), "?"
        )
        return f"{t.due_datetime.strftime('%I:%M %p')} | {pet_name} | {t.title}"

    task_labels  = [task_label(t) for t in all_incomplete]
    chosen_label = st.selectbox("Select a task to complete", task_labels, key="complete_select")
    chosen_task  = all_incomplete[task_labels.index(chosen_label)]

    if st.button("Mark complete"):
        pet_obj = next(
            (p for p in owner.pets if any(x.id == chosen_task.id for x in p.tasks)), None
        )
        if pet_obj:
            next_task = scheduler.mark_task_complete(chosen_task.id, pet_obj)
            st.success(f"'{chosen_task.title}' marked complete.")
            if next_task:
                st.info(
                    f"Recurring task detected — next '{next_task.title}' "
                    f"auto-scheduled for "
                    f"{next_task.due_datetime.strftime('%A, %b %d at %I:%M %p')}."
                )

# ---------------------------------------------------------------------------
# Section 5 — Today's Schedule (sorted by time + conflict warnings)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Today's Schedule")

scheduler.load_from_owner(owner)   # pick up any tasks added this session
todays = scheduler.sort_by_time(scheduler.get_todays_tasks())

# --- Conflict warnings first — most actionable info goes at the top ---
conflicts = scheduler.get_conflict_warnings(owner)
if conflicts:
    st.error(f"**{len(conflicts)} scheduling conflict(s) detected — please review before your day starts.**")
    for msg in conflicts:
        st.warning(msg)

# --- Schedule table ---
if not todays:
    st.info("No incomplete tasks due today.")
else:
    st.success(f"{len(todays)} task(s) on today's agenda for {owner.name}.")
    st.table([
        {
            "Time":     t.due_datetime.strftime("%I:%M %p"),
            "Pet":      next((p.name for p in owner.pets
                              if any(x.id == t.id for x in p.tasks)), "?"),
            "Task":     t.title,
            "Type":     t.task_type.value,
            "Priority": f"P{t.priority}",
            "Recurs":   t.recurrence.value if t.recurrence != Recurrence.NONE else "—",
            "Notes":    t.notes or "—",
        }
        for t in todays
    ])

# ---------------------------------------------------------------------------
# Section 6 — Filter view
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Filter Tasks")

if not owner.pets:
    st.info("Add pets and tasks to use the filter.")
else:
    col1, col2 = st.columns(2)
    with col1:
        filter_pet    = st.selectbox("Filter by pet",
                                     ["All pets"] + [p.name for p in owner.pets],
                                     key="filter_pet")
    with col2:
        filter_status = st.selectbox("Filter by status",
                                     ["All", "Incomplete", "Complete"],
                                     key="filter_status")

    filtered = list(scheduler.tasks)

    if filter_pet != "All pets":
        filtered = scheduler.filter_by_pet(filtered, filter_pet, owner)

    if filter_status == "Incomplete":
        filtered = scheduler.filter_by_status(filtered, complete=False)
    elif filter_status == "Complete":
        filtered = scheduler.filter_by_status(filtered, complete=True)

    filtered = scheduler.sort_by_time(filtered)

    if filtered:
        st.caption(f"{len(filtered)} task(s) match your filters.")
        st.table([
            {
                "Date":     t.due_datetime.strftime("%Y-%m-%d"),
                "Time":     t.due_datetime.strftime("%I:%M %p"),
                "Pet":      next((p.name for p in owner.pets
                                  if any(x.id == t.id for x in p.tasks)), "?"),
                "Task":     t.title,
                "Type":     t.task_type.value,
                "Priority": f"P{t.priority}",
                "Done":     "Yes" if t.is_complete else "No",
            }
            for t in filtered
        ])
    else:
        st.info("No tasks match the selected filters.")
# ---------------------------------------------------------------------------
# Section 7 — Ask PawPal AI
# ---------------------------------------------------------------------------
st.divider()
st.subheader("🤖 Ask PawPal AI")

if not owner.pets:
    st.info("Add a pet first before using the AI advisor.")
else:
    st.caption("Ask a care question about one of your pets. PawPal will retrieve relevant knowledge and give you a personalized answer.")

    ai_pet = st.selectbox("Which pet is your question about?", [p.name for p in owner.pets], key="ai_pet")
    ai_question = st.text_input("Your question", placeholder="e.g. Can Buddy eat grapes? How often should Luna visit the vet?")

    if st.button("Ask PawPal"):
        if not ai_question.strip():
            st.warning("Please enter a question.")
        else:
            pet_obj = next(p for p in owner.pets if p.name == ai_pet)

            with st.spinner("PawPal is thinking..."):
                from rag_advisor import ask_pawpal
                result = ask_pawpal(
                    question=ai_question,
                    pet_name=pet_obj.name,
                    species=pet_obj.species,
                    breed=pet_obj.breed,
                    age=pet_obj.age,
                    weight=pet_obj.weight,
                )

            st.markdown("**PawPal's Answer:**")
            st.write(result["answer"])
            st.caption(result["confidence"])
