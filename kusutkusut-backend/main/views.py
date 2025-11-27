from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Tweet, Person
from django.db.models import Count
from django.utils import timezone

User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(password) < 6:
        return Response({"detail": "Password must be at least 6 characters long."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the user
    user = User.objects.create_user(username=username, password=password)
    
    # Also create a Person entry for this user so they can be an author
    # This is not strictly in the TODO but necessary for the app's logic
    if not Person.objects.filter(username=username).exists():
        Person.objects.create(name=username, username=username)

    return Response({"message": "registered"}, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
    
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    try:
        person = Person.objects.get(username=request.user.username)
        return Response({
            "id": person.id,
            "name": person.name,
            "username": person.username,
            "profile_picture": person.profile_picture.url if person.profile_picture else None,
            "bio": person.bio,
            "followers": person.followers.count(),
            "following": person.following.count(),
            "joined_date": person.joined_date.strftime("%B %Y")
        })
    except Person.DoesNotExist:
        return Response({"detail": "Person profile not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def secret(request):
    """
    TODO:
    Buat function bebas, sekreatif atau sekocak mungkin
    Examples:
    - Return random number
    - Return custom message
    - Return a JSON list of your favorite movies
    - Return https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ
    - Anything
    """

    # original track URLs (may include query params). We'll convert them to embed URLs
    songs = [
        "https://open.spotify.com/track/6BV77pE4JyUQUtaqnXeKa5?si=c97fb92b44734eae",
        "https://open.spotify.com/track/2Xztg4QQc8x8MK6I7TuIV7?si=5b855bab95e141da",
        "https://open.spotify.com/track/4XHijJfABTtUCW3Bp6KFvr?si=559c1531b1a54ec5",
    ]

    # Convert to embed URLs and strip query parameters for clean embed src
    embed_songs = []
    for url in songs:
        base = url.split('?')[0]
        embed = base.replace('/track/', '/embed/track/')
        embed_songs.append(embed)

    context = {
        'name': 'sigmoby',
        'message': '6 7',
        'song_list': embed_songs,
    }

    return render(request, "spotify.html", context)

@api_view(["GET"])
@permission_classes([AllowAny])
def hello(request):
    return Response({"message": "Hello, world!"}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def tweets_list(request):
    """
    GET: Return all tweets sorted by published_date (newest first).
    POST: Create a new tweet. Requires authentication.
    """
    if request.method == "GET":
        # Get all tweets ordered newest first
        # annotate with replies count to avoid extra DB queries per tweet
        tweets = Tweet.objects.select_related('author').annotate(
            replies_count=Count('comments'),
            likes_count=Count('liked_by')
        )
        
        username = request.query_params.get('username')
        if username:
            tweets = tweets.filter(author__username=username)

        tweets = tweets.order_by('-published_date')

        # Check if current user liked the tweet
        # We can't easily annotate boolean with standard Django without Case/When or Exists
        # Simpler approach for now: iterate and check if user is authenticated
        
        user = request.user
        is_authenticated = user.is_authenticated
        current_person = None
        if is_authenticated:
            try:
                current_person = Person.objects.get(username=user.username)
            except Person.DoesNotExist:
                pass

        data = []
        for t in tweets:
            author = t.author
            is_liked = False
            if current_person:
                is_liked = t.liked_by.filter(id=current_person.id).exists()

            data.append({
                'id': t.id,
                'content': t.content,
                'likes': t.likes_count,
                'is_liked': is_liked,
                'replies_count': t.replies_count,
                'published_date': t.published_date.isoformat() if t.published_date else None,
                'author': {
                    'id': author.id,
                    'name': author.name,
                    'username': author.username,
                    'profile_picture': author.profile_picture.url if author.profile_picture else None,
                },
                'parent_tweet': t.parent_tweet.id if t.parent_tweet else None,
            })

        return Response(data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        if not request.user.is_authenticated:
             return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        content = request.data.get("content")
        if not content:
            return Response({"detail": "Content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            author = Person.objects.get(username=request.user.username)
        except Person.DoesNotExist:
             return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        tweet = Tweet.objects.create(
            content=content,
            author=author,
            published_date=timezone.now()
        )

        # Serialize the new tweet
        data = {
            'id': tweet.id,
            'content': tweet.content,
            'likes': tweet.liked_by.count(),
            'replies_count': 0,
            'published_date': tweet.published_date.isoformat(),
            'author': {
                'id': author.id,
                'name': author.name,
                'username': author.username,
                'profile_picture': author.profile_picture.url if author.profile_picture else None,
            },
            'parent_tweet': None,
        }

        return Response(data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_tweet(request, tweet_id):
    try:
        tweet = Tweet.objects.get(id=tweet_id)
        person = Person.objects.get(username=request.user.username)
    except (Tweet.DoesNotExist, Person.DoesNotExist):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if tweet.liked_by.filter(id=person.id).exists():
        tweet.liked_by.remove(person)
        liked = False
    else:
        tweet.liked_by.add(person)
        liked = True
    
    return Response({
        "liked": liked,
        "likes_count": tweet.liked_by.count()
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    username = request.query_params.get('username')
    if not username:
        return Response({"detail": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile_user = Person.objects.get(username=username)
        current_user_person = Person.objects.get(username=request.user.username)
    except Person.DoesNotExist:
        return Response({"detail": "Person profile not found."}, status=status.HTTP_404_NOT_FOUND)

    is_following = current_user_person.following.filter(id=profile_user.id).exists()

    return Response({
        "id": profile_user.id,
        "name": profile_user.name,
        "username": profile_user.username,
        "profile_picture": profile_user.profile_picture.url if profile_user.profile_picture else None,
        "bio": profile_user.bio,
        "followers": profile_user.followers.count(),
        "following": profile_user.following.count(),
        "joined_date": profile_user.joined_date.strftime("%B %Y"),
        "is_following": is_following,
        "is_self": profile_user.id == current_user_person.id
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    try:
        target_user = Person.objects.get(username=username)
        current_user_person = Person.objects.get(username=request.user.username)
    except Person.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if target_user.id == current_user_person.id:
        return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if current_user_person.following.filter(id=target_user.id).exists():
        current_user_person.following.remove(target_user)
        following = False
    else:
        current_user_person.following.add(target_user)
        following = True

    return Response({
        "following": following,
        "followers_count": target_user.followers.count()
    }, status=status.HTTP_200_OK)

@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def tweet_detail(request, tweet_id):
    try:
        tweet = Tweet.objects.get(id=tweet_id)
    except Tweet.DoesNotExist:
        return Response({"detail": "Tweet not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check permission: only author can edit/delete
    try:
        person = Person.objects.get(username=request.user.username)
    except Person.DoesNotExist:
        return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

    if tweet.author != person:
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "PUT":
        content = request.data.get("content")
        if not content:
            return Response({"detail": "Content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        tweet.content = content
        tweet.save()
        return Response({"id": tweet.id, "content": tweet.content}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        tweet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)